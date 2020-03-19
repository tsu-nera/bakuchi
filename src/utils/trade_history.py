import os
import pandas as pd
import datetime
import src.utils.json as json
from statistics import mean

from tabulate import tabulate

import src.utils.private as private
import src.constants.path as path
import src.constants.ccxtconst as ccxtconst
import src.utils.datetime as dt


def _create_trade(id, order_id, datetime, pair, side, fee, amount, price,
                  rate):
    return {
        "id": int(id),
        "order_id": int(order_id),
        "datetime": datetime,
        "pair": pair,
        "side": side,
        "fee": fee,
        "amount": round(float(amount), 3),
        "price": round(abs(float(price)), 3),
        "rate": round(float(rate), 3)
    }


def _convert_coincheck_datetime(d_str):
    timestamp = datetime.datetime.fromisoformat(d_str.replace('Z', ''))
    timestamp = timestamp + datetime.timedelta(hours=9)
    return timestamp.strftime(dt.DATETIME_BASE_FORMAT)


def _get_latest_file_name(exchange_id):
    return "latest_trades_{}.csv".format(exchange_id)


def _marge_duplicated_trades(trades):
    dup = [trade['datetime'] for trade in trades]
    dup_count_list = [dup.count(x) for x in dup]

    filterd_trades = []

    i = 0
    while i < len(dup):
        n = dup_count_list[i]
        if n > 1:
            current_trade = trades[i]
            total_amount = sum([trades[i + j]["amount"] for j in range(n)])
            total_price = sum([trades[i + j]["price"] for j in range(n)])
            average_rate = mean([trades[i + j]["rate"] for j in range(n)])

            merged_trade = _create_trade(
                current_trade["id"], current_trade["order_id"],
                current_trade["datetime"], current_trade["pair"],
                current_trade["side"], current_trade["fee"], total_amount,
                total_price, average_rate)
            filterd_trades.append(merged_trade)
        else:
            trade = trades[i]
            filterd_trades.append(trade)
        i += n

    return filterd_trades


def _format_coincheck_trades(data):
    trades = []
    for t in data:
        trade = _create_trade(t["id"], t["order_id"],
                              _convert_coincheck_datetime(t["created_at"]),
                              t["pair"], t["side"], float(t["fee"]),
                              float(t["funds"]["btc"]),
                              float(t["funds"]["jpy"]), float(t["rate"]))
        trades.append(trade)

    return _marge_duplicated_trades(trades)


def _format_fetched_trades(data):
    trades = []

    for t in data:
        created_at = datetime.datetime.fromtimestamp(t["created_at"])
        timestamp = dt.format_timestamp(created_at)

        trade = _create_trade(t["id"], t["order_id"], timestamp, t["pair"],
                              t["taker_side"], 0, t["quantity"], t["price"],
                              t["rate"])
        trades.append(trade)
    return _marge_duplicated_trades(trades)


def fetch_trades(exchange_id):
    trades = private.fetch_trades(exchange_id)

    if exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
        trades = _format_coincheck_trades(trades)
    else:
        trades = _format_fetched_trades(trades)

    return trades


def save_trades(exchange_id):
    '''
    取引履歴をcsvに保存
    '''
    trades = fetch_trades(exchange_id)

    file_name = _get_latest_file_name(exchange_id)
    file_path = os.path.join(path.TRADES_RAWDATA_DIR_PATH, file_name)

    df = pd.DataFrame.from_dict(trades)
    df.to_csv(file_path, index=None)


def show_recent_profits(hours=None):
    cc_trades = fetch_trades(ccxtconst.EXCHANGE_ID_COINCHECK)
    lq_trades = fetch_trades(ccxtconst.EXCHANGE_ID_LIQUID)

    # print([trade["datetime"] for trade in cc_trades])
    # print([trade["datetime"] for trade in lq_trades])

    if len(cc_trades) < len(lq_trades):
        base_trades = cc_trades
        target_trades = lq_trades
        base_exchange_id = ccxtconst.EXCHANGE_ID_COINCHECK
        target_exchange_id = ccxtconst.EXCHANGE_ID_LIQUID
    else:
        base_trades = lq_trades
        target_trades = cc_trades
        base_exchange_id = ccxtconst.EXCHANGE_ID_LIQUID
        target_exchange_id = ccxtconst.EXCHANGE_ID_COINCHECK

    def _to_dict(trades):
        trade_dict = {}
        for trade in trades:
            trade_dict[trade["datetime"]] = trade
        return trade_dict

    base_trade_dict = _to_dict(base_trades)
    target_trade_dict = _to_dict(target_trades)

    summary = []
    for timestamp, data in base_trade_dict.items():
        if hours:
            datetime_threshold = datetime.datetime.now() - datetime.timedelta(
                hours=hours)

            datetime_timestamp = datetime.datetime.strptime(
                timestamp, dt.DATETIME_BASE_FORMAT)

            if datetime_timestamp < datetime_threshold:
                continue

        try:
            target_data = target_trade_dict[timestamp]
            base_data = data

            info = {}
            info["timestamp"] = timestamp
            if base_data['side'] == 'buy':
                info['buy_id'] = base_exchange_id
                info['sell_id'] = target_exchange_id
                info['buy_price'] = int(base_data['price'])
                info['sell_price'] = int(target_data['price'])
            else:
                info['buy_id'] = target_exchange_id
                info['sell_id'] = base_exchange_id
                info['buy_price'] = int(target_data['price'])
                info['sell_price'] = int(base_data['price'])
            info["profit"] = int(info["sell_price"] - info['buy_price'])
        except Exception:
            continue

        summary.append(info)

    profits = [x['profit'] for x in summary]
    total_profit = sum(profits)
    total_trade_count = len(summary)

    timestamp_first = summary[0]["timestamp"]
    timestamp_last = summary[-1]["timestamp"]

    if timestamp_first < timestamp_last:
        oldest_timestamp = timestamp_first
        latest_timestamp = timestamp_last
    else:
        oldest_timestamp = timestamp_last
        latest_timestamp = timestamp_first

    print("期間: {} - {}".format(oldest_timestamp, latest_timestamp))
    print("取引回数: {}".format(total_trade_count))
    print("利益: {}".format(total_profit))

    table = []
    table.append(["日時", "売却取引所", "売値", "購入取引所", "買値", "利益"])

    for x in summary:
        table_row = [
            x["timestamp"], x["buy_id"], x["buy_price"], x["sell_id"],
            x["sell_price"], x["profit"]
        ]
        table.append(table_row)

    print(tabulate(table, headers="firstrow"))


def backup_trades():
    from_dir_path = path.TRADES_RAWDATA_DIR_PATH

    for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
        from_file_name = _get_latest_file_name(exchange_id)

        from_file_path = os.path.join(from_dir_path, from_file_name)

        convert_trades(from_file_path, exchange_id)


def _get_datetime_range(start_datetime, end_datetime):
    start_date = start_datetime.date()
    end_date = end_datetime.date()

    date_list = []
    index_date = start_date

    while index_date <= end_date:
        date_list.append(index_date)
        index_date += datetime.timedelta(days=1)

    return date_list


def read_trades(path):
    return pd.read_csv(path, index_col="id",
                       parse_dates=["datetime"]).sort_values('datetime')


def _read_trades(timestamp, exchange_id):
    file_name = "{}.csv".format(exchange_id)
    file_path = os.path.join(path.REPORTS_DIR, timestamp, path.TRADES_DIR,
                             file_name)
    return read_trades(file_path)


def read_coincheck(timestamp):
    exchange_id = ccxtconst.EXCHANGE_ID_COINCHECK
    return _read_trades(timestamp, exchange_id)


def read_liquid(timestamp):
    exchange_id = ccxtconst.EXCHANGE_ID_LIQUID
    return _read_trades(timestamp, exchange_id)


def convert_trades(from_path, exchange_id):
    df = read_trades(from_path)

    start_datetime = df.iloc[0]['datetime']
    end_datetime = df.iloc[-1]['datetime']

    date_range = _get_datetime_range(start_datetime, end_datetime)

    for date in date_range:
        dir_name = date.strftime('%y%m%d')
        to_dir_path = os.path.join(path.TRADES_DATA_DIR_PATH, dir_name)

        if not os.path.exists(to_dir_path):
            os.mkdir(to_dir_path)

        to_file_name = "{}.csv".format(exchange_id)
        to_file_path = os.path.join(to_dir_path, to_file_name)

        df_date = df[df.datetime.dt.date == date]

        if os.path.exists(to_file_path):
            df_old = read_trades(to_file_path)
            df_new = pd.concat([df_old, df_date], sort=False).drop_duplicates(
                subset=["datetime"]).sort_values("datetime")
        else:
            df_new = df_date

        df_new.to_csv(to_file_path)


def create_profit_df(cc_df, lq_df):
    df = pd.DataFrame({
        'timestamp': cc_df['datetime'].to_list(),
        'cc_side': cc_df['side'].to_list(),
        'cc_price': cc_df['price'].to_list(),
        'lq_side': lq_df['side'].to_list(),
        'lq_price': lq_df['price'].to_list()
    })

    def calc_profit(x):
        if x['cc_side'] == 'sell':
            cc_price = x['cc_price']
        else:
            cc_price = -1 * x['cc_price']

        if x['lq_side'] == 'sell':
            lq_price = x['lq_price']
        else:
            lq_price = -1 * x['lq_price']

        return cc_price + lq_price

    df['profit'] = df.apply(calc_profit, axis=1)

    df.timestamp = pd.to_datetime(df.timestamp, format=dt.DATETIME_BASE_FORMAT)
    df = df.set_index('timestamp')

    return df


def read_trade_asset(keyword, timestamp):
    file_name = "{}.json".format(keyword)
    file_path = os.path.join(path.REPORTS_DIR, timestamp, path.ASSETS_DIR,
                             file_name)
    return json.read(file_path)


def display_report(timestamp):
    display_asset_report(timestamp)


def display_asset_report(timestamp):
    start_asset = read_trade_asset('start', timestamp)
    end_asset = read_trade_asset('end', timestamp)

    def _format(v):
        return round(v, 3)

    def _get_total_jpy(asset):
        return round(
            asset['total']['jpy'] + sum([
                asset[exchange_id]['btc'] * asset[exchange_id]['bid']
                for exchange_id in ccxtconst.EXCHANGE_ID_LIST
            ]), 3)

    actual_start_total_jpy = _get_total_jpy(start_asset)
    actual_end_total_jpy = _get_total_jpy(end_asset)
    actual_profit_jpy = round(actual_end_total_jpy - actual_start_total_jpy, 3)

    notrade_start_total_jpy = actual_start_total_jpy
    notrade_end_total_jpy = round(
        start_asset['total']['jpy'] + sum([
            start_asset[exchange_id]['btc'] * end_asset[exchange_id]['bid']
            for exchange_id in ccxtconst.EXCHANGE_ID_LIST
        ]), 3)
    notrade_profit_jpy = round(notrade_end_total_jpy - notrade_start_total_jpy,
                               3)

    trade_profit_jpy = actual_profit_jpy - notrade_profit_jpy
    time_profit_jpy = notrade_profit_jpy

    profits = []
    profits.append(['Bot利益', 'トレード利益', '市場利益'])
    profits.append([actual_profit_jpy, trade_profit_jpy, time_profit_jpy])

    print(tabulate(profits, headers="firstrow"))

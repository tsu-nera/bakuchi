import os
import pandas as pd
import datetime

import src.utils.private as private
import src.constants.common as common
import src.constants.ccxtconst as ccxtconst


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
        "price": round(float(price), 3),
        "rate": round(float(rate), 3)
    }


def _convert_coincheck_datetime(d_str):
    dt = datetime.datetime.fromisoformat(d_str.replace('Z', ''))
    dt = dt + datetime.timedelta(hours=9)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def _format_coincheck_trades(data):
    trades = []
    for t in data:
        trade = _create_trade(t["id"], t["order_id"],
                              _convert_coincheck_datetime(t["created_at"]),
                              t["pair"], t["side"], float(t["fee"]),
                              float(t["funds"]["btc"]),
                              float(t["funds"]["jpy"]), float(t["rate"]))
        trades.append(trade)

    dup = [trade['datetime'] for trade in trades]
    dup_flag_list = [True if dup.count(x) > 1 else False for x in dup]

    filterd_trades = []

    i = 0
    while i < len(dup):
        flag = dup_flag_list[i]
        if flag:
            current_trade = trades[i]
            next_trade = trades[i + 1]
            merged_trade = _create_trade(
                current_trade["id"], current_trade["order_id"],
                current_trade["datetime"], current_trade["pair"],
                current_trade["side"], current_trade["fee"],
                current_trade["amount"] + next_trade["amount"],
                current_trade["price"] + next_trade["price"],
                (current_trade["rate"] + next_trade["rate"]) / 2)
            i += 2
            filterd_trades.append(merged_trade)
        else:
            trade = trades[i]
            filterd_trades.append(trade)
            i += 1

    return filterd_trades


def _format_fetched_trades(trades):
    res = []

    for t in trades:
        timestamp = datetime.datetime.fromtimestamp(t["created_at"])

        trade = _create_trade(t["id"], t["order_id"], timestamp, t["pair"],
                              t["taker_side"], 0, t["quantity"], t["price"], 0)
        res.append(trade)

    return res


def save_trades(exchange_id):
    '''
    取引履歴をcsvに保存
    '''
    trades = private.fetch_trades(exchange_id)

    if exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
        trades = _format_coincheck_trades(trades)
    else:
        trades = _format_fetched_trades(trades)

    file_name = "latest_trades_{}.csv".format(exchange_id)
    file_path = os.path.join(common.TRADES_RAWDATA_DIR_PATH, file_name)

    df = pd.DataFrame.from_dict(trades)
    df.to_csv(file_path, index=None)

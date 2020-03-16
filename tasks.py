from invoke import task, run
import importlib
import psutil
from distutils.dir_util import copy_tree

import src.utils.public as public
import src.utils.private as private

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks
import src.utils.tool as tool
import src.utils.trade_history as trade_history
from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient

import src.constants.ccxtconst as ccxtconst
import src.config as config

import logging
from logging import basicConfig
basicConfig(level=logging.INFO, handlers=[])

TRADING_MODULE = importlib.import_module('src.utils.trading')
PUBLIC_MODULE = importlib.import_module('src.utils.public')


@task
def tick_bitflyer(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_BITFLYER)


@task
def tick_coincheck(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_COINCHECK)


@task
def tick_liquid(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_LIQUID)


@task
def tick_bitbank(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_BITBANK)


@task
def tick_bitmex(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_BITMEX, ccxtconst.SYMBOL_BTC_USD)


@task
def tick_testnet(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_BITMEX_DEMO,
                       ccxtconst.SYMBOL_BTC_USD)


@task
def tick_gemini_sandbox(c):
    public.fetch_ticks(ccxtconst.EXCHANGE_ID_GEMINI_DEMO,
                       ccxtconst.SYMBOL_BTC_USD)


@task
def balance_bitflyer(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_BITFLYER))


@task
def balance_coincheck(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_COINCHECK))


@task
def balance_liquid(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_LIQUID))


@task
def balance_bitbank(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_BITBANK))


@task
def balance_testnet(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_BITMEX_DEMO))


@task
def balance_gemini_sandbox(c):
    print(private.fetch_balance(ccxtconst.EXCHANGE_ID_GEMINI_DEMO))


@task
def trade(c):
    run_trading()


@task
def demo_trade(c):
    run_trading(demo_mode=True)


@task
def backtest(c, timestamp):
    run_backtesting(timestamp)


@task
def simulate(c, timestamp):
    run_backtesting(timestamp, simulate_mode=True)


@task
def get_historical_data(c):
    save_ticks()


@task
def symbols(c, exchange_id):
    c = CcxtClient(exchange_id)
    print(c.symbols())


@task
def buy_with_amount(c, exchange_id, amount):
    response = private.create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                        float(amount))
    print(response)
    return response


@task
def buy(c, exchange_id):
    return buy_with_amount(c, exchange_id, config.TRADE_AMOUNT)


@task
def sell_with_amount(c, exchange_id, amount):
    response = private.create_sell_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                         float(amount))
    print(response)
    return response


@task
def sell(c, exchange_id):
    return sell_with_amount(c, exchange_id, config.TRADE_AMOUNT)


@task
def sell_coincheck_with_amount(c, amount):
    client = CcxtClient(ccxtconst.EXCHANGE_ID_COINCHECK)
    tick = client.fetch_tick()
    bid = float(tick["bid"])

    response = private.create_sell_order(ccxtconst.EXCHANGE_ID_COINCHECK,
                                         ccxtconst.SYMBOL_BTC_JPY,
                                         float(amount), bid)
    print(response)
    return response


@task
def sell_coincheck(c):
    return sell_coincheck_with_amount(c, config.TRADE_AMOUNT)


@task
def buy_coincheck_with_amount(c, amount):
    client = CcxtClient(ccxtconst.EXCHANGE_ID_COINCHECK)
    tick = client.fetch_tick()
    ask = float(tick["ask"])

    response = private.create_buy_order(ccxtconst.EXCHANGE_ID_COINCHECK,
                                        ccxtconst.SYMBOL_BTC_JPY,
                                        float(amount), ask)
    print(response)
    return response


@task
def buy_coincheck(c):
    return buy_coincheck_with_amount(c, config.TRADE_AMOUNT)


@task
def sell_liquid_with_amount(c, amount):
    return sell_with_amount(c, ccxtconst.EXCHANGE_ID_LIQUID, amount)


@task
def sell_liquid(c):
    return sell(c, ccxtconst.EXCHANGE_ID_LIQUID)


@task
def buy_liquid_with_amount(c, amount):
    return buy_with_amount(c, ccxtconst.EXCHANGE_ID_LIQUID, amount)


@task
def buy_liquid(c):
    return buy(c, ccxtconst.EXCHANGE_ID_LIQUID)


@task
def buy_coincheck_sell_liquid(c):
    cc_jpy = int(buy_coincheck(c)["jpy"])
    lq_jpy = int(sell_liquid(c)["jpy"])

    print("buy coincheck {}, sell liquid {}, profit={}".format(
        cc_jpy, lq_jpy, lq_jpy - cc_jpy))


@task
def sell_coincheck_buy_liquid(c):
    cc_jpy = int(sell_coincheck(c)["jpy"])
    lq_jpy = int(buy_liquid(c)["jpy"])

    print("buy liquid {}, sell coincheck {}, profit={}".format(
        lq_jpy, cc_jpy, cc_jpy - lq_jpy))


@task
def buy_testnet(c):
    private.create_buy_order(ccxtconst.EXCHANGE_ID_BITMEX_DEMO,
                             ccxtconst.SYMBOL_BTC_USD, 1)


@task
def sell_testnet(c):
    private.create_sell_order(ccxtconst.EXCHANGE_ID_BITMEX_DEMO,
                              ccxtconst.SYMBOL_BTC_USD, 1)


@task
def fetch_orders(c):
    private.fetch_open_orders(ccxtconst.EXCHANGE_ID_BITMEX_DEMO)
    private.fetch_open_orders(ccxtconst.EXCHANGE_ID_COINCHECK)
    private.fetch_open_orders(ccxtconst.EXCHANGE_ID_LIQUID)


@task
def fetch_positions(c):
    private.get_positions(ccxtconst.EXCHANGE_ID_BITMEX_DEMO)
    private.get_positions(ccxtconst.EXCHANGE_ID_COINCHECK)
    private.get_positions(ccxtconst.EXCHANGE_ID_LIQUID)


@task
def save_coincheck_trades(c):
    trade_history.save_trades(ccxtconst.EXCHANGE_ID_COINCHECK)


@task
def save_liquid_trades(c):
    trade_history.save_trades(ccxtconst.EXCHANGE_ID_LIQUID)


@task
def save_trades(c):
    save_coincheck_trades(c)
    save_liquid_trades(c)


###############
# Utils
###############
@task
def check_margin(c):
    tool.check_profit_margin()


@task
def asset(c):
    tool.check_asset()


@task
def calc_btcjpy(c, btc_amount):
    tool.calc_btc_to_jpy(float(btc_amount))


@task
def calc_jpybtc(c, jpy_price):
    tool.calc_jpy_to_btc(int(jpy_price))


# @task
def reload(c):
    # 検証中
    importlib.reload(PUBLIC_MODULE)


@task
def recent_profits(c):
    trade_history.show_recent_profits()


@task
def recent_profits_by(c, hour):
    trade_history.show_recent_profits(hour)


###############
# Othre Utils
###############
@task
def backup_data(c, dir_name):
    production_dir = "../bakuchi_production/data/historicals/"
    from_dir = production_dir + dir_name
    to_dir = "data/backtests/" + dir_name

    copy_tree(from_dir, to_dir)


@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")


@task
def slack(c, message):
    client = SlackClient()
    client.notify_with_datetime(message)


@task
def is_trade(c):
    flag = any([
        p.cmdline()[2] == "trade" for p in psutil.process_iter()
        if len(p.cmdline()) == 3
    ])

    if flag:
        print("trading bot is running.")
    else:
        print("trading bot is stopped.")

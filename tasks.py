from invoke import task, run

import os
import glob
import time
import datetime

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
import src.utils.report as report
from src.utils.trade_analysis import run_analysis

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient
from src.libs.asset import Asset

import src.constants.path as path
import src.constants.ccxtconst as ccxtconst
import src.config as config
import src.env as env

import logging
from logging import basicConfig

basicConfig(level=logging.INFO, handlers=[])

TRADING_MODULE = importlib.import_module('src.utils.trading')
PUBLIC_MODULE = importlib.import_module('src.utils.public')


@task
def ping_coincheck(c):
    tool.ping(ccxtconst.EXCHANGE_ID_COINCHECK)


@task
def ping_liquid(c):
    tool.ping(ccxtconst.EXCHANGE_ID_LIQUID)


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
def bot(c):
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
    response = private.create_coincheck_sell_order(ccxtconst.SYMBOL_BTC_JPY,
                                                   float(amount))
    print(response)
    return response


@task
def sell_coincheck(c):
    return sell_coincheck_with_amount(c, config.TRADE_AMOUNT)


@task
def buy_coincheck_with_amount(c, amount):
    response = private.create_coincheck_buy_order(ccxtconst.SYMBOL_BTC_JPY,
                                                  float(amount))
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
    Asset().display()


@task
def bot_asset(c):
    Asset().run_bot()


@task
def calc_btcjpy(c, btc_amount):
    Asset().calc_btc_to_jpy(float(btc_amount))


@task
def calc_jpybtc(c, jpy_price):
    Asset().calc_jpy_to_btc(int(jpy_price))


# @task
def reload(c):
    # 検証中
    importlib.reload(PUBLIC_MODULE)


@task
def recent_profits(c):
    trade_history.show_recent_profits()


@task
def recent_profits_by(c, hour):
    trade_history.show_recent_profits(int(hour))


@task
def trade_analysis(c, timestamp):
    run_analysis(timestamp)


@task
def trade_latest_analysis(c):
    dir_path = path.REPORTS_DIR
    timestamp = get_latest_dirname(dir_path)
    run_analysis(timestamp)


@task
def display_report(c, timestamp):
    report.display(timestamp)


@task
def display_latest_report(c):
    dir_path = path.REPORTS_DIR
    timestamp = get_latest_dirname(dir_path)
    report.display(timestamp)


###############
# Othre Utils
###############
def get_latest_dirpath(dir_path):
    return max(glob.glob(os.path.join(dir_path, '*/')), key=os.path.getmtime)


def get_latest_dirname(dir_path):
    file_path = get_latest_dirpath(dir_path)
    return os.path.basename(os.path.dirname(file_path))


@task
def backup_latest_data(c):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = get_latest_dirpath(production_dir)
    dir_name = from_dir.split('/')[-2]
    to_dir = os.path.join(path.BACKTEST_DATA_DIR_PATH, dir_name)

    copy_tree(from_dir, to_dir)


@task
def backup_data(c, dir_name):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = os.path.join(production_dir, dir_name)
    to_dir = os.path.join(path.BACKTEST_DATA_DIR_PATH, dir_name)

    copy_tree(from_dir, to_dir)


@task
def generate_report(c, dir_name):
    report.generate(dir_name)


@task
def run_notebook(c, file_path):
    report.run_notebook(file_path)


@task
def export_trade_result(c, timestamp):
    report.export_trade_result(timestamp)


@task
def generate_latest_report(c):
    report.generate_latest()


@task
def backup_trades(c):
    trade_history.backup_trades()


@task
def note(c):
    run("jupyter notebook --notebook-dir='.'")


@task
def slack(c, message):
    url = env.SLACK_WEBHOOK_URL_TRADE
    client = SlackClient(url)
    client.notify_with_datetime(message)


@task
def check_error(c):
    root_dir_path = "./data/historicals"
    dir_path = get_latest_dirpath(root_dir_path)
    run('find {} -type f -name "*.log" | xargs grep ERROR'.format(dir_path))


@task
def is_bot(c):
    flag = any([
        p.cmdline()[2] == "trade" for p in psutil.process_iter()
        if len(p.cmdline()) == 3
    ])

    if flag:
        print("trading bot is running.")
    else:
        print("trading bot is stopped.")


@task
def adjust_coincheck_buy_amount(c):
    tool.adjust_coincheck_buy_amount()


###############
# perf tools
###############


def perf_func_execution_time(func):
    start_time = datetime.datetime.now()
    func()
    end_time = datetime.datetime.now()

    exec_time_ms = round((end_time - start_time).microseconds / 1000, 2)

    return exec_time_ms


@task
def perf_fetch_tick(c):
    def fetch_tick_with_serial():
        ret1 = public.fetch_tick(ccxtconst.EXCHANGE_ID_COINCHECK)
        ret2 = public.fetch_tick(ccxtconst.EXCHANGE_ID_LIQUID)

        return ret1, ret2

    for _ in range(10):
        time_ms = perf_func_execution_time(lambda: tool.ping_with_thread())
        print("get tick parallel time={} ms".format(time_ms))
        time.sleep(1)

        time_ms = perf_func_execution_time(fetch_tick_with_serial)
        print("get tick serial   time={} ms".format(time_ms))
        time.sleep(1)

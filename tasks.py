from invoke import task, run

import src.utils.public as public
import src.utils.private as private

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks
import src.utils.tool as tool
from src.libs.ccxt_client import CcxtClient

import src.constants.ccxtconst as ccxtconst
from src.config import config

import logging
from logging import basicConfig
basicConfig(level=logging.INFO, handlers=[])

ORDER_AMOUNT = float(config["trade"]["amount"])


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
    private.fetch_balance(ccxtconst.EXCHANGE_ID_BITMEX_DEMO)


@task
def balance_gemini_sandbox(c):
    private.fetch_balance(ccxtconst.EXCHANGE_ID_GEMINI_DEMO)


@task
def trade(c):
    run_trading()


@task
def backtest(c, timestamp):
    run_backtesting(timestamp)


@task
def get_historical_data(c):
    save_ticks()


@task
def symbols(c, exchange_id):
    c = CcxtClient(exchange_id)
    print(c.symbols())


@task
def sell_coincheck(c):
    private.create_sell_order(ccxtconst.EXCHANGE_ID_COINCHECK, ORDER_AMOUNT)


@task
def buy_coincheck(c):
    client = CcxtClient(ccxtconst.EXCHANGE_ID_COINCHECK)
    tick = client.fetch_tick()
    ask = float(tick["ask"])

    private.create_buy_order(ccxtconst.EXCHANGE_ID_COINCHECK, ORDER_AMOUNT,
                             ask)


@task
def sell_liquid(c):
    private.create_sell_order(ccxtconst.EXCHANGE_ID_LIQUID, ORDER_AMOUNT)


@task
def buy_liquid(c):
    private.create_buy_order(ccxtconst.EXCHANGE_ID_LIQUID, ORDER_AMOUNT)


@task
def buy_coincheck_sell_liquid(c):
    buy_coincheck(c)
    sell_liquid(c)


@task
def sell_coincheck_buy_liquid(c):
    sell_coincheck(c)
    buy_liquid(c)


@task
def buy_testnet(c):
    private.create_buy_order(ccxtconst.EXCHANGE_ID_BITMEX_DEMO, 1)


@task
def sell_testnet(c):
    private.create_sell_order(ccxtconst.EXCHANGE_ID_BITMEX_DEMO, 1)


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


###############
# Utils
###############
@task
def check_margin(c):
    tool.check_profit_margin()


@task
def check_asset(c):
    tool.check_asset()


@task
def calc_btcjpy(c, btc_amount):
    tool.calc_btc_to_jpy(float(btc_amount))


@task
def calc_jpybtc(c, jpy_price):
    tool.calc_jpy_to_btc(int(jpy_price))


###############
# Othre Utils
###############
@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")

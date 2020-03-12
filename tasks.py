from invoke import task, run

from src.experiments.public import fetch_ticks
from src.experiments.private import fetch_balance, create_buy_order, create_sell_order

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks
from src.libs.ccxt_client import CcxtClient

import src.constants.ccxtconst as cctxconst

from logging import basicConfig

basicConfig(filename="logs/bakuchi.log")


@task
def tick_bitflyer(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def tick_coincheck(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def tick_liquid(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_LIQUID)


@task
def tick_bitbank(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_BITBANK)


@task
def tick_bitmex(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_BITMEX, cctxconst.SYMBOL_BTC_USD)


@task
def tick_testnet(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_BITMEX_DEMO, cctxconst.SYMBOL_BTC_USD)


@task
def tick_gemini_sandbox(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_GEMINI_DEMO, cctxconst.SYMBOL_BTC_USD)


@task
def balance_bitflyer(c):
    fetch_balance(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def balance_coincheck(c):
    fetch_balance(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def balance_liquid(c):
    fetch_balance(cctxconst.EXCHANGE_ID_LIQUID)


@task
def balance_bitbank(c):
    fetch_balance(cctxconst.EXCHANGE_ID_BITBANK)


@task
def balance_testnet(c):
    fetch_balance(cctxconst.EXCHANGE_ID_BITMEX_DEMO)


@task
def balance_gemini_sandbox(c):
    fetch_balance(cctxconst.EXCHANGE_ID_GEMINI_DEMO)


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
def buy_testnet(c):
    create_buy_order(cctxconst.EXCHANGE_ID_BITMEX_DEMO, 1)


@task
def sell_testnet(c):
    create_sell_order(cctxconst.EXCHANGE_ID_BITMEX_DEMO, 1)


###############
# Othre Utils
###############
@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")

from invoke import task, run

import src.utils.public as public
import src.utils.private as private

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks
from src.libs.ccxt_client import CcxtClient

import src.constants.ccxtconst as cctxconst

from logging import basicConfig

basicConfig(filename="logs/bakuchi.log")


@task
def tick_bitflyer(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def tick_coincheck(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def tick_liquid(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_LIQUID)


@task
def tick_bitbank(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_BITBANK)


@task
def tick_bitmex(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_BITMEX, cctxconst.SYMBOL_BTC_USD)


@task
def tick_testnet(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_BITMEX_DEMO,
                       cctxconst.SYMBOL_BTC_USD)


@task
def tick_gemini_sandbox(c):
    public.fetch_ticks(cctxconst.EXCHANGE_ID_GEMINI_DEMO,
                       cctxconst.SYMBOL_BTC_USD)


@task
def balance_bitflyer(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def balance_coincheck(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def balance_liquid(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_LIQUID)


@task
def balance_bitbank(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_BITBANK)


@task
def balance_testnet(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_BITMEX_DEMO)


@task
def balance_gemini_sandbox(c):
    private.fetch_balance(cctxconst.EXCHANGE_ID_GEMINI_DEMO)


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
    private.create_buy_order(cctxconst.EXCHANGE_ID_BITMEX_DEMO, 1)


@task
def sell_testnet(c):
    private.create_sell_order(cctxconst.EXCHANGE_ID_BITMEX_DEMO, 1)


@task
def fetch_orders(c):
    private.fetch_open_orders(cctxconst.EXCHANGE_ID_BITMEX_DEMO)


@task
def fetch_positions(c):
    private.get_positions(cctxconst.EXCHANGE_ID_BITMEX_DEMO)


###############
# Othre Utils
###############
@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")

from invoke import task, run

from src.experiments.public import fetch_ticks
from src.experiments.private import fetch_balance

from src.utils.trading import run_trading
from src.utils.backtesting import run_backtesting
from src.utils.historical import save_ticks

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
def trade(c):
    run_trading()


@task
def backtest(c, date):
    run_backtesting(date)


@task
def get_historical_data(c):
    save_ticks()


###############
# Othre Utils
###############
@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")

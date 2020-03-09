from invoke import task, run

from src.experiments.public import fetch_ticks
from src.experiments.private import fetch_balance
from src.experiments.arbitrage import trade
from src.utils.historical import save_ticks

import src.constants.ccxtconst as cctxconst

from logging import basicConfig

basicConfig(filename="logs/bakuchi.log")


@task
def note(c):
    run("jupyter notebook --notebook-dir='notebooks'")


@task
def tick_bitflyer(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def tick_coincheck(c):
    fetch_ticks(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def balance_bitflyer(c):
    fetch_balance(cctxconst.EXCHANGE_ID_BITFLYER)


@task
def balance_coincheck(c):
    fetch_balance(cctxconst.EXCHANGE_ID_COINCHECK)


@task
def arbitrage(c):
    trade()


@task
def get_historical_data(c):
    save_ticks()

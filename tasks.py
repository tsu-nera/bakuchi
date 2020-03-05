from invoke import task

from src.experiments.public import fetch_ticks
from src.experiments.private import fetch_balance

import src.constants.ccxtconst as cctxconst


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

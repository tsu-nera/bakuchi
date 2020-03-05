from invoke import task

from src.experiments.public import fetch_ticks
from src.experiments.private import fetch_bitflyer_balance


@task
def balance(c):
    fetch_bitflyer_balance()


@task
def tick_bitflyer(c):
    fetch_ticks("bitflyer")


@task
def tick_coincheck(c):
    fetch_ticks("coincheck")

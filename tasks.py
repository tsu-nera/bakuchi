from invoke import task

from src.experiments.public import fetch_bitflyer_ticks
from src.experiments.private import fetch_bitflyer_balance


@task
def balance(c):
    fetch_bitflyer_balance()


@task
def tick(c):
    fetch_bitflyer_ticks()

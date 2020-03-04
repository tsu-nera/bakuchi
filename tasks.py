from invoke import task
from src.experiments.ticker import bitflyer


@task
def tick(c):
    bitflyer()

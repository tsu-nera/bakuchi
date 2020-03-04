import invoke
from src.experiments.client import bitflyer


@invoke.task
def tmp(c):
    bitflyer()

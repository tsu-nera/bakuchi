import pandas as pd

from src.drivers.driver import Driver


class CsvDriver(Driver):
    def __init__(self):
        pass

    def read_df(self, path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

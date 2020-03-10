import pandas as pd


class CsvDriver():
    def __init__(self):
        pass

    def read_df(self, path):
        return pd.read_csv(path, index_col=0, parse_dates=True)

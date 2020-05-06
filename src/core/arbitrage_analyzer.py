from statistics import mean

from src.config import OPEN_THRESHOLD_CHANGE_SEC, TRADE_TICK_INTERVAL_SEC


class ArbitrageAnalyzer():
    def __init__(self, open_threshold_change_sec=None):
        self.reset()

        if open_threshold_change_sec:
            self.open_threshold_change_sec = open_threshold_change_sec
        else:
            self.open_threshold_change_sec = OPEN_THRESHOLD_CHANGE_SEC

    def reset(self):
        self.buyx_selly_margings = []
        self.buyy_sellx_margings = []
        self.length = 0

    def update(self, a, b):
        self.buyx_selly_margings.append(a)
        self.buyy_sellx_margings.append(b)
        self.length += TRADE_TICK_INTERVAL_SEC

    def check_period(self):
        return self.length > self.open_threshold_change_sec

    def check_period_for_logging(self):
        return self.length >= self.open_threshold_change_sec

    def get_new_open_threshold(self):
        sample_length = 90
        length = int((self.open_threshold_change_sec - sample_length) /
                     TRADE_TICK_INTERVAL_SEC)
        buyx_selly_mean = mean(self.buyx_selly_margings[length:])
        buyy_sellx_mean = mean(self.buyy_sellx_margings[length:])

        threshold = int(max(buyx_selly_mean, buyy_sellx_mean))

        if threshold < 2000:
            new_threshold = 2000
        else:
            new_threshold = threshold

        return new_threshold

    def update_open_threshold_change_sec(self, value):
        if value:
            self.open_threshold_change_sec = value

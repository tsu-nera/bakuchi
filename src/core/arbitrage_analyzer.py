from src.config import PROFIT_MARGIN_THRESHOLD_CHANGE_SEC
from statistics import mean


class ArbitrageAnalyzer():
    def __init__(self):
        self.reset()

    def reset(self):
        self.buyx_selly_margings = []
        self.buyy_sellx_margings = []
        self.length = 0

    def update(self, a, b):
        self.buyx_selly_margings.append(a)
        self.buyy_sellx_margings.append(b)
        self.length += 1

    def check_period(self):
        return self.length > PROFIT_MARGIN_THRESHOLD_CHANGE_SEC

    def check_period_for_logging(self):
        return self.length >= PROFIT_MARGIN_THRESHOLD_CHANGE_SEC

    def get_new_profit_margin_threshold(self):
        buyx_selly_mean = mean(self.buyx_selly_margings)
        buyy_sellx_mean = mean(self.buyy_sellx_margings)

        threshold = int(max(buyx_selly_mean, buyy_sellx_mean))

        if threshold < 1000:
            new_threshold = 1000
        else:
            new_threshold = threshold

        return new_threshold

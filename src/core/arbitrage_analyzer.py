from src.config import OPEN_THRESHOLD_CHANGE_SEC
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
        return self.length > OPEN_THRESHOLD_CHANGE_SEC

    def check_period_for_logging(self):
        return self.length >= OPEN_THRESHOLD_CHANGE_SEC

    def get_new_open_threshold(self):
        sample_length = 90
        length = OPEN_THRESHOLD_CHANGE_SEC - sample_length
        buyx_selly_mean = mean(self.buyx_selly_margings[length:])
        buyy_sellx_mean = mean(self.buyy_sellx_margings[length:])

        threshold = int(max(buyx_selly_mean, buyy_sellx_mean))

        if threshold < 1000:
            new_threshold = 1000
        else:
            new_threshold = threshold

        return new_threshold

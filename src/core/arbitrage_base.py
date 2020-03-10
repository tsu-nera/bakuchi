from abc import ABCMeta, abstractmethod


class ArbitrageBase(metaclass=ABCMeta):
    STRATEGY_BUY_X_AND_SELL_Y = "buy x and sell y"
    STRATEGY_BUY_Y_AND_SELL_X = "buy y and sell x"
    STRATEGY_DO_NOTHING = "do nothing"

    @abstractmethod
    def run(self):
        pass

    def next(self):
        # tick取得
        x, y = self._get_tick()

        # 判定
        result = self._evaluate(x, y)

        # アクション
        self._action(result, x, y)

    @abstractmethod
    def _get_tick(self):
        pass

    def _evaluate(self, x, y):
        if y.bid > x.ask:
            return self.STRATEGY_BUY_X_AND_SELL_Y
        elif x.bid > y.ask:
            return self.STRATEGY_BUY_Y_AND_SELL_X
        else:
            return self.STRATEGY_DO_NOTHING

    @abstractmethod
    def _action(self, result, x, y):
        pass

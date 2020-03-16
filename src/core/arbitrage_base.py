from abc import ABCMeta, abstractmethod
from src.core.arbitrage_analyzer import ArbitrageAnalyzer


class ArbitrageBase(metaclass=ABCMeta):
    STRATEGY_BUY_X_AND_SELL_Y = "buy x and sell y"
    STRATEGY_BUY_Y_AND_SELL_X = "buy y and sell x"
    STRATEGY_DO_NOTHING = "no strategy"

    def __init__(self):
        self._reset_action_permission()
        self.analyzer = ArbitrageAnalyzer()

    @abstractmethod
    def run(self):
        pass

    def next(self):
        # tick取得
        x, y = self._get_tick()

        if x and y:
            # 判定
            result = self._evaluate(x, y)

            # アクション
            self._action(result, x, y)

    @abstractmethod
    def _get_tick(self):
        pass

    def _evaluate(self, x, y):
        self.analyzer.update(y.bid - x.ask, x.bid - y.ask)
        if self.analyzer.check_period():
            self.profit_margin_threshold = self.analyzer.get_new_profit_margin_threshold(
            )
            self.analyzer.reset()

        if self._check_action_permission_buyx_selly(y.bid, x.ask):
            return self.STRATEGY_BUY_X_AND_SELL_Y
        elif self._check_action_permission_buyy_sellx(x.bid, y.ask):
            return self.STRATEGY_BUY_Y_AND_SELL_X
        else:
            return self.STRATEGY_DO_NOTHING

    @abstractmethod
    def _action(self, result, x, y):
        pass

    def _update_entry_profit_margin(self, value):
        if self.action_permission:
            self.entry_profit_margin = value
        else:
            self.entry_profit_margin = None

    def _check_profit_margin_threshold(self, bid, ask):
        return bid - ask > self.profit_margin_threshold

    def _check_profit_margin_diff_allowed(self, bid, ask):
        return bid - ask > self.profit_margin_diff - self.entry_profit_margin

    def _check_action_permission_buyx_selly(self, bid, ask):
        if self.action_permission:
            return self._check_profit_margin_threshold(bid, ask)
        else:
            if self._check_profit_margin_diff_allowed(bid, ask):
                return self.action_direction
            else:
                return False

    def _check_action_permission_buyy_sellx(self, bid, ask):
        if self.action_permission:
            return self._check_profit_margin_threshold(bid, ask)
        else:
            if self._check_profit_margin_diff_allowed(bid, ask):
                return not self.action_direction
            else:
                return False

    def _rearrange_action_permission_buyx_selly(self):
        if self.action_permission:
            self._allow_only_buyy_sellx()
        else:
            self._reset_action_permission()

    def _rearrange_action_permission_buyy_sellx(self):
        if self.action_permission:
            self._allow_only_buyx_selly()
        else:
            self._reset_action_permission()

    def _reset_action_permission(self):
        self.action_permission = True
        self.action_direction = None

    def _allow_only_buyx_selly(self):
        self.action_permission = False
        self.action_direction = True

    def _allow_only_buyy_sellx(self):
        self.action_permission = False
        self.action_direction = False

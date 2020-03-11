from abc import ABCMeta, abstractmethod


class ArbitrageBase(metaclass=ABCMeta):
    STRATEGY_BUY_X_AND_SELL_Y = "buy x and sell y"
    STRATEGY_BUY_Y_AND_SELL_X = "buy y and sell x"
    STRATEGY_DO_NOTHING = "no strategy"

    def __init__(self):
        self._reset_action_permission()

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
        if y.bid > x.ask:
            return self.STRATEGY_BUY_X_AND_SELL_Y
        elif x.bid > y.ask:
            return self.STRATEGY_BUY_Y_AND_SELL_X
        else:
            return self.STRATEGY_DO_NOTHING

    @abstractmethod
    def _action(self, result, x, y):
        pass

    def _check_action_permission_buyx_selly(self):
        if self.action_permission:
            return True
        else:
            return self.action_direction

    def _check_action_permission_buyy_sellx(self):
        if self.action_permission:
            return True
        else:
            return not self.action_direction

    def _reset_action_permission(self):
        self.action_permission = True
        self.action_direction = None
 
    def _allow_only_buyx_selly(self):
        self.action_permission = False
        self.action_direction = True

    def _allow_only_buyy_sellx(self):
        self.action_permission = False
        self.action_direction = False
        
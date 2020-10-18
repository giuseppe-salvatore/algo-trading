class TradeMgt():

    def __init__(self):
        self.stop_loss = None
        self.take_target = None

    def has_stop_loss(self):
        return (True if self.stop_loss is not None else False)

    def has_take_target(self):
        return (True if self.take_target is not None else False)

    def set_stop_loss(self, value: float):
        self.stop_loss = value

    def set_take_target(self, value: float):
        self.take_target = value

class NoMgt(TradeMgt):

    def __init__(self):
        super().__init__()

class FixedLevelsTradeMgt(TradeMgt):

    def __init__(self, entry_level, stop_loss, take_target):
        super().__init__()
        self.entry_level
        self.set_stop_loss(stop_loss)
        self.set_take_target(take_target)

class RiskRewardRatioTradeMgt(TradeMgt):

    def __init__(self, entry_level, stop_loss, risk_reward_ratio):
        super().__init__()
        self.entry_level
        self.set_stop_loss(stop_loss)
        self.set_take_target(entry_level + (abs(entry_level-stop_loss)*risk_reward_ratio)

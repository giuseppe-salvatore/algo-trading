

class TradingManagmentPolicy():
    def __init__(self):
        pass

    def get_trading_policy(self, name, configuration):
        pass

class TradingPolicy():

    def __init__(self, config):
        self.config = config
        self._validate_config()

    def get_config(self):
        return self.config

    def is_managed(self):
        pass

    def is_dynamic(self):
        pass

    def _validate_config(self):
        pass

class Unmanaged():
    def is_managed(self):
        return False

    def is_dynamic(self):
        return False

    def _validate_config(self):
        return True

class StaticPolicy():
    def __init__(self, config):
        self.confg = config

    def is_managed(self):
        return False

    def is_dynamic(self):
        return False

    def _validate_config(self):
        pass


class PriceDrivenPolicy():
    def __init__(self):
        pass

    def set_rr_ratio(self, ratio):
        self.rr_ratio = ratio

    def get_reward_price(self, pull_back_price, last_price, side):
        if side == 'buy':
            if pull_back_price >= last_price - or
                return abs(last_price - pull_back_price) * self.rr_ratio

        if side == 'sell':
            return abs(last_price - pull_back_price) * self.rr_ratio

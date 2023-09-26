from lib.indicators.base_indicator import Indicator

default_params = {
    "period": 14,
    "mean_period": 4,
    "mean_type": "SMA",
    "source": "close"
}


class RelativeStrenghtIndex(Indicator):

    def __init__(self, params=default_params):
        super().__init__()
        self.short_name = "RSI"
        self.long_name = "Relative Strenght Index"
        self.description = "An inicator that goes between 0 and 100 that takes \
                            into accout the strenght of the price action"

        self.set_params(params)

    @staticmethod
    def get_default_params():
        return default_params

    def set_param(self, key, val):
        self.params[key] = val
        self._update_name()

    def set_params(self, val):
        self.params = val
        self._update_name()

    def _update_name(self):
        self.name = "{} {} {}".format("RSI", self.params["period"],
                                      self.params["source"])

    def calculate(self, data):
        source = data[self.params["source"]]
        delta = source.diff()
        up = delta.copy().rolling(window=self.params["mean_period"]).mean()
        down = delta.copy().rolling(window=self.params["mean_period"]).mean()
        up[up < 0] = 0
        down[down > 0] = 0

        roll_up = None
        roll_down = None
        # Calculate the RSI based on EWMA
        if self.params["mean_type"] == 'EMA':
            roll_up = up.ewm(span=self.params["period"]).mean()
            roll_down = down.abs().ewm(span=self.params["period"]).mean()

        # Calculate the RSI based on SMA
        elif self.params["mean_type"] == 'SMA':
            # Calculate the SMA
            roll_up = up.rolling(self.params["period"]).mean()
            roll_down = down.abs().rolling(self.params["period"]).mean()

        else:
            raise Exception("Mean type parameter can only be EMA or SMA")

        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        return rsi

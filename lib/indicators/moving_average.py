from lib.indicators.base_indicator import Indicator

default_params = {
    "mean_period": 200,
    "mean_type": "SMA",
    "source": "close"
}

class MovingAverage(Indicator):

    def __init__(self, params=default_params):
        super().__init__()
        self.short_name = "MA"
        self.description = "An inicator that goes between 0 and 100 that takes \
                            into accout the strenght of the price action"
        self.set_params(params)

    @staticmethod
    def get_default_params():
        return default_params

    def set_params(self, val):
        self.params = val
        self._update_name()

    def set_param(self, key, val):
        self.params[key] = val
        self._update_name()

    def _update_name(self):
        self.name = "{} {} {}".format(
            self.params["mean_type"],
            self.params["mean_period"],
            self.params["source"]
        )

    @property
    def indicator_type(self):
        if self.params["mean_type"] == "SMA":
            return "Simple Moving Average"
        elif self.params["mean_type"] == "EMA":
            return "Exponential Moving Average"
        else:
            raise ValueError("Unknown mean type")

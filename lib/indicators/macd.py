import itertools
import pandas as pd
from lib.indicators.base_indicator import Indicator

default_params = {
    "long_mean_period": 26,
    "short_mean_period": 12,
    "mean_type": "EMA",
    "signal_smooth": 9,
    "source": "close"
}

class MACD(Indicator):

    def __init__(self, params=default_params):
        super().__init__()
        self.short_name = "MACD"
        self.long_name = "Relative Strenght Index"
        self.description = "An inicator that goes between 0 and 100 that takes \
                            into accout the strenght of the price action"
        # Swith to use of dot notation:
        # https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary/41274937#41274937
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
        self.name = "{} {} {} {} {}".format(
            "MACD",
            self.params["short_mean_period"],
            self.params["long_mean_period"],
            self.params["signal_smooth"],
            self.params["source"]
        )

    def calculate(self, data):
        source = data[self.params["source"]]

        short_mean = source.copy().ewm(span=self.params["short_mean_period"], adjust=False).mean()
        long_mean = source.copy().ewm(span=self.params["long_mean_period"], adjust=False).mean()

        # Calculate the Moving Average Convergence/Divergence (MACD)
        macd = short_mean - long_mean

        # Calcualte the signal line
        signal = macd.ewm(span=self.params["signal_smooth"], adjust=False).mean()

        self.data = pd.DataFrame({"signal": signal, "macd": macd, "histogram": macd - signal})
        return self.data

    def generate_param_combination(self, size):

        params = []
        if size == 'small':
            long_mean_period = [26, 30]
            short_mean_period = [12, 14]
            signal_mean_period = [9, 10]
            mean_type = ["SMA", "EMA"]
            source = ["close"]
        else:
            long_mean_period = [26]
            short_mean_period = [12]
            signal_mean_period = [9]
            mean_type = ["SMA"]
            source = ["close"]

        param_product = itertools.product(
            long_mean_period,
            short_mean_period,
            mean_type,
            source,
            signal_mean_period
        )

        for param in param_product:
            params.append({
                'long_mean_period': param[0],
                'short_mean_period': param[1],
                'mean_type': param[2],
                'source': param[3],
                "signal_mean_period": param[4]
            })

        return params

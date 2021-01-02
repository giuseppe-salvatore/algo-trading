import pandas as pd
from lib.indicators.base_indicator import Indicator

default_params = {
    "source": "close"
}


def _vwap(df):
    q = df["volume"].values
    p = df["close"].values
    return df.assign(vwap=(p * q).cumsum() / q.cumsum())

class VWAP(Indicator):

    def __init__(self, params=default_params):
        super().__init__()
        self.short_name = "VWAP"
        self.long_name = "Volume Weighted Average Price"
        self.description = "An moving average that takes into account the volume together with the price action"
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
        self.name = "{} {}".format(
            "VWAP",
            self.params["source"]
        )

    def calculate(self, data):
        data = data.groupby(data.index, group_keys=False).apply(_vwap)
        vwap = data["vwap"].copy()

        self.data = pd.DataFrame({"vwap": vwap})
        return self.data

    def generate_param_combination(self, size):
        pass

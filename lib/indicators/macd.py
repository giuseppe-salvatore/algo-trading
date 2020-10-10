import pandas as pd
import itertools as itl
from lib.indicators.base_indicator import Indicator

# logging.basicConfig(level='WARNING')
# log = logging.getLogger(__name__)
# log.setLevel('DEBUG')

class MACD(Indicator):

    def __init__(self):
        super().__init__()
        self.short_name = "rsi"
        self.long_name = "Relative Strenght Index"
        self.description = "An inicator that goes between 0 and 100 that takes \
                            into accout the strenght of the price action"
        self.params = {
            "long_mean_period": 26,
            "short_mean_period": 12,
            "mean_type": "SMA",
            "signal_mean_period": 9,
            "source": "close"
        }

    def calculate(self, data):
        source = data[self.params["source"]]

        short_mean = source.copy().ewm(span=self.params["short_mean_period"], adjust=False).mean()
        long_mean = source.copy().ewm(span=self.params["long_mean_period"], adjust=False).mean()

        # Calculate the Moving Average Convergence/Divergence (MACD)
        macd = short_mean - long_mean

        # Calcualte the signal line
        signal = macd.ewm(span=self.params["signal_mean_period"], adjust=False).mean()

        df = pd.DataFrame({"signal": signal, "macd": macd, "histogram": macd - signal})
        return df

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

        param_product = itl.product(
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

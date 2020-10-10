from lib.indicators.base_indicator import Indicator

# logging.basicConfig(level='WARNING')
# log = logging.getLogger(__name__)
# log.setLevel('DEBUG')

class RelativeStrenghtIndex(Indicator):

    def __init__(self):
        super().__init__()
        self.short_name = "rsi"
        self.long_name = "Relative Strenght Index"
        self.description = "An inicator that goes between 0 and 100 that takes \
                            into accout the strenght of the price action"
        self.params = {
            "period": 14,
            "mean_period": 4,
            "mean_type": "SMA",
            "source": "close"
        }

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

import pandas as pd
from lib.indicators.base_indicator import Indicator

# logging.basicConfig(level='WARNING')
# log = logging.getLogger(__name__)
# log.setLevel('DEBUG')


class BollingerBands(Indicator):

    def __init__(self):
        super().__init__()
        self.short_name = "rsi"
        self.long_name = "Bollinger Bands"
        self.description = "Two bands which enclose the price action and  \
                            expand/contract based on that"

        self.params = {
            "stddev_factor": 2,
            "mean_period": 9,
            "mean_type": "SMA",
            "source": "close"
        }

    def calculate(self, data):
        source = self.params["source"]
        mean_period = self.params["mean_period"]
        stddev_factor = self.params["stddev_factor"]

        bb_mean = data[source].copy().rolling(window=mean_period).mean()

        # data.assign(
        #     change=np.where(
        #         diffs > 0, 1, np.where(
        #         diffs < 0, -1, 0)
        #     )
        # )

        df = pd.DataFrame({"bb_mean": bb_mean})

        df["bb_up"] = df["bb_mean"] + stddev_factor * data[source].rolling(
            window=mean_period).std()
        df["bb_down"] = df["bb_mean"] - stddev_factor * \
            data[source].rolling(window=mean_period).std()
        df["band_spread"] = df["bb_up"] - df["bb_down"]

        return df

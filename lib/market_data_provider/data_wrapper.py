import datetime
import pandas as pd

from lib.market_data_provider.finnhub import FinnhubDataProvider
import lib.util.logger as logger
logger.setup_logging("MarketData")
log = logger.logging.getLogger("MarketData")


provider = FinnhubDataProvider()

class MarketData():

    def __init__(self):
        self._data: pd.Dataframe = None
        self._resoluton = None
        self._start = None
        self._end = None

    def get_data(self,
                 symbol: str,
                 start_datetime: datetime,
                 end_datetime: datetime,
                 resolution: str = "minute",
                 res_multipier: int = 1):

        if res_multipier != 1:
            msg = "Feature not supported, resolution multiplier must be 1"
            log.error(msg)
            raise ValueError(msg)

        # We neet to fetch the data if:
        # - we dont' have it at all
        # - we have it but at the wrong resolution or a timeframe that
        #   isn't contained in the one we have
        fetch_data = False
        if self._data is None:
            fetch_data = True
        else:
            if start_datetime < self._start or \
               end_datetime > self._end or \
               self._resoluton != resolution:
                fetch_data = True

        if fetch_data is True:
            if resolution == "minute":
                self._data = provider.get_minute_candles(symbol, start_datetime, end_datetime)
                self._resoluton = "1 min"
                self._start = start_datetime
                self._end = end_datetime
                return self._data
            elif resolution == "day":
                # self._data = provider.get_day_candles(symbol, start_datetime, end_datetime)
                pass
            else:
                msg = "{} resolution not supported".format(resolution)
                log.error(msg)
                raise ValueError(msg)
        else:
            return self._data.between_time(start_datetime, end_datetime)

    def _combine_data(self):
        pass

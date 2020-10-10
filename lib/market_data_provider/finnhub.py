import time
import pandas as pd
import conf.secret as config
from datetime import datetime
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.market_data_provider import MarketDataProvider, MarketDataUtils


candle_endpoint = "/v1/stock/candle"


class FinnhubDataProvider(MarketDataProvider):

    def __init__(self):
        self.set_provider_name("Finnhub")
        self.set_provider_url("https://finnhub.io")
        self.set_base_url("https://finnhub.io/api")

    def get_key_name(self):
        return "token"

    def get_key_value(self):
        return config.FINNHUB_API_KEY

    def _transform_to_dataframe(self, json_res):
        result_list = []
        result_lengh = len(json_res["c"])

        for i in range(result_lengh):
            date_time = datetime.fromtimestamp(int(json_res["t"][i]))

            result_list.append({
                "datetime": date_time.strftime("%Y-%m-%d %H:%M"),
                "open": json_res["o"][i],
                "high": json_res["h"][i],
                "low": json_res["l"][i],
                "close": json_res["c"][i],
                "volume": json_res["v"][i]
            })

        df = pd.DataFrame(result_list)
        df.set_index("datetime", inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M', exact=False)
        return df

    def get_minute_candles(self,
                           symbol: str,
                           start_date: datetime,
                           end_date: datetime,
                           force_provider_fetch: bool = False,
                           store_fetched_data: bool = False):
        """
        Example: https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=1&from=1572651390&to=1572910590

        Arguments:

        token: apiKey

        symbol: REQUIRED
        Symbol.

        resolution: REQUIRED
        Supported resolution includes 1, 5, 15, 30, 60, D, W, M .
        Some timeframes might not be available depending on the exchange.

        from: REQUIRED
        UNIX timestamp. Interval initial value. (use datetime.fromtimestamp(from))

        to: REQUIRED
        UNIX timestamp. Interval end value.

        format: optional
        By default, format=json. Strings json and csv are accepted.

        adjusted: optional
        By default, adjusted=false. Use true to get adjusted data.

        """

        # Finnhub uses UNIX timestapms to operate with time ranges so we need to convert to datetime
        start_date = MarketDataUtils.from_string_to_datetime(start_date)
        end_date = MarketDataUtils.from_string_to_datetime(end_date)

        if force_provider_fetch is False:
            log.debug("Loading candles from db for {} time between {} {}".format(
                symbol,
                start_date,
                end_date
            ))
            db = DBManager()
            df = db.minute_candles_to_dataframe(symbol, start_date, end_date)
            print(df)
            if MarketDataUtils.check_candles_in_timeframe(df, start_date, end_date):
                db.close()
                log.debug("Successfully fetched {} candles ".format(df.shape[0]))
                return df
            else:
                log.warning("No candles available in db, fetching from data provider")

        log.debug("Fetching minute candles on " + self.get_provider_name() + " api")

        start_date = str(int(time.mktime(start_date.timetuple())))
        end_date = str(int(time.mktime(end_date.timetuple())))

        endpoint = candle_endpoint
        params = {
            "symbol": symbol,
            "resolution": "1",
            "format": "json",
            "from": start_date,
            "to": end_date,
            "adjusted": True
        }

        res = self.get(endpoint, params)

        try:
            json_res = res.json()
        except Exception as e:
            log.error("Response not in json format " + res.text)
            log.error(e)
            return None

        df = self._transform_to_dataframe(json_res)

        if store_fetched_data is True:
            try:
                db.dataframe_to_minute_candles(symbol, df)
            except Exception as e:
                log.error("Failed to store data in db: {}".format(e))

        return df

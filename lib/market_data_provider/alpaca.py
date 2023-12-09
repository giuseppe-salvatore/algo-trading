import os
import pytz
import time
import pandas as pd
import conf.secret as config
from datetime import datetime
from datetime import timedelta
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.market_data_provider import MarketDataProvider, MarketDataUtils

candle_endpoint = "/v1/stock/candle"
news_endpoint = "/v1/company-news"
splits_endpoint = "/v1/stock/split"


def to_unix_ts(date_time: str):
    date_time = MarketDataUtils.from_string_to_datetime(date_time)
    return str(int(time.mktime(date_time.timetuple())))


class FinnhubDataProvider(MarketDataProvider):

    def __init__(self):
        self.set_provider_name("Finnhub")
        self.set_provider_url("https://finnhub.io")
        self.set_base_url("https://finnhub.io/api")
        self.api_key = os.environ.get('FINNHUB_API_KEY')
        if self.api_key is None:
            self.api_key = config.FINNHUB_API_KEY

    def get_key_name(self):
        return "token"

    def get_key_value(self):
        return self.api_key

    def _transform_to_dataframe(self, json_res, native_tz=False):
        result_list = []
        result_lengh = len(json_res["c"])

        for i in range(result_lengh):
            if native_tz:
                date_time = datetime.fromtimestamp(
                    int(json_res["t"][i]), pytz.timezone('America/New_York'))
            else:
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
        df.index = pd.to_datetime(df.index,
                                  format='%Y-%m-%d %H:%M',
                                  exact=False)
        return df

    def get_news(self, symbol: str, start_date: datetime, end_date: datetime):
        start_date = to_unix_ts(start_date)
        end_date = to_unix_ts(end_date)

        endpoint = news_endpoint
        params = {"symbol": symbol, "from": start_date, "to": end_date}

        return self.get(endpoint, params)

    def get_splits(self, symbol: str, start_date: str, end_date: str):

        endpoint = splits_endpoint
        params = {"symbol": symbol, "from": start_date, "to": end_date}

        res = self.get(endpoint, params)
        try:
            json_res = res.json()
        except Exception as e:
            log.error("Response not in json format " + res.text)
            log.error(e)
            return None

        return json_res

    def get_market_news(self):
        pass

    def get_candles(self,
                    symbol: str,
                    start_date: datetime,
                    end_date: datetime,
                    time_frame: dict,
                    force_provider_fetch: bool = False,
                    store_fetched_data: bool = False):

        tf = time_frame["multiplier"]
        tf += time_frame["timeframe"]

        if time_frame["timeframe"] == "Min":
            df = self.get_minute_candles(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_provider_fetch=force_provider_fetch,
                store_fetched_data=store_fetched_data)
        elif time_frame["timeframe"] == "Day":
            df = self.get_daily_candles(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_provider_fetch=force_provider_fetch,
                store_fetched_data=store_fetched_data)
        else:
            raise ValueError("Unexpected time frame candle specificed ")

        log.debug("Getting candles for {}".format(tf))

        # The result dataframe will be grouping rows based on the timeframe
        # and getting min/max for low/high and first/last for open/close
        # as a resulting aggregated candle
        result_df = pd.DataFrame()
        result_df["open"] = df.groupby(pd.Grouper(freq=tf))["open"].first()
        result_df["close"] = df.groupby(pd.Grouper(freq=tf))["close"].last()
        result_df["high"] = df.groupby(pd.Grouper(freq=tf))["high"].max()
        result_df["low"] = df.groupby(pd.Grouper(freq=tf))["low"].min()
        result_df["volume"] = df.groupby(pd.Grouper(freq=tf))["volume"].sum()

        return result_df

    def get_daily_candles(self,
                          symbol: str,
                          start_date: datetime,
                          end_date: datetime,
                          force_provider_fetch: bool = False,
                          store_fetched_data: bool = False):
        pass

    def get_minute_candles(self,
                           symbol: str,
                           start_date: datetime,
                           end_date: datetime,
                           force_provider_fetch: bool = False,
                           store_fetched_data: bool = False):
        """
        Example: https://finnhub.io/api/v1/stock/candle?
                 symbol=AAPL&resolution=1&from=1572651390&to=1572910590

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
        UNIX timestamp. Interval end value. (NOTE: this is excluded except
                        for the first candle of this day at 00:00)

        format: optional
        By default, format=json. Strings json and csv are accepted.

        adjusted: optional
        By default, adjusted=false. Use true to get adjusted data.

        """

        # Finnhub uses UNIX timestapms to operate with time ranges so we need to convert to datetime
        start_date = MarketDataUtils.from_string_to_datetime(start_date)
        end_date = MarketDataUtils.from_string_to_datetime(end_date)
        end_date = end_date + timedelta(days=1)

        if force_provider_fetch is False:
            log.debug(
                "Loading candles from db for {} time between {} {}".format(
                    symbol, start_date, end_date))
            db = DBManager()
            df = db.minute_candles_to_dataframe(symbol, start_date, end_date)
            if MarketDataUtils.check_candles_in_timeframe(
                    df, start_date, end_date):
                db.close()
                log.debug("Successfully fetched {} candles ".format(
                    df.shape[0]))
                df["ny_datetime"] = df.index - pd.DateOffset(hours=4)
                return df
            else:
                log.warning(
                    "No candles available in db, fetching from data provider")

        log.debug("Fetching minute candles on " + self.get_provider_name() +
                  " api")
        end_date_filter = end_date.replace(hour=0, minute=0)
        start_date = str(int(time.mktime(start_date.timetuple())))
        end_date = str(int(time.mktime(end_date.timetuple())))

        endpoint = candle_endpoint
        params = {
            "symbol": symbol,
            "resolution": "1",
            "format": "json",
            "from": start_date,
            "to": end_date,
            "adjusted": "true"
        }

        res = self.get(endpoint, params)

        try:
            json_res = res.json()
        except Exception as e:
            log.error("Response not in json format " + res.text)
            log.error(e)
            return None

        df = self._transform_to_dataframe(json_res, native_tz=True)
        df.drop(pd.Timestamp(end_date_filter), inplace=True, errors='ignore')

        if store_fetched_data is True:
            try:
                db = DBManager()
                db.dataframe_to_minute_candles(symbol, df)
                db.close()
            except Exception as e:
                log.error("Failed to store data in db: {}".format(e))

        return df

import pytz
import time
import pandas as pd
from datetime import datetime
from datetime import timedelta
from lib.util.logger import log
from lib.db.manager import DBManager
# from alpaca.data.timeframe import TimeFrame
# from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient
from conf.secret import ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET
from lib.market_data_provider.market_data_provider import (
    MarketDataProvider,
    MarketDataUtils,
)

candle_endpoint = "/v1/stock/candle"
news_endpoint = "/v1/company-news"
splits_endpoint = "/v1/stock/split"

# The following is commented out because the linter was complaining
# but it looks like this piece of code is not used

# request_params = StockBarsRequest(
#     symbol_or_symbols=symbol,
#     timeframe=TimeFrame.Minute,
#     start=date[0],
#     end=date[1],
# )

# bars = client.get_stock_bars(request_params)


def to_unix_ts(date_time: str):
    date_time = MarketDataUtils.from_string_to_datetime(date_time)
    return str(int(time.mktime(date_time.timetuple())))


class AlpacaDataProvider(MarketDataProvider):
    def __init__(self):
        self.set_provider_name("Alpaca")
        self.set_provider_url(None)
        self.set_base_url(None)
        self.client = StockHistoricalDataClient(ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET)

    def get_key_name(self):
        return "token"

    def get_key_value(self):
        return ALPACA_LIVE_API_KEY

    def _transform_to_dataframe(self, json_res, native_tz=False):
        result_list = []
        result_length = len(json_res["c"])

        for i in range(result_length):
            if native_tz:
                date_time = datetime.fromtimestamp(
                    int(json_res["t"][i]), pytz.timezone("America/New_York")
                )
            else:
                date_time = datetime.fromtimestamp(int(json_res["t"][i]))

            result_list.append(
                {
                    "datetime": date_time.strftime("%Y-%m-%d %H:%M"),
                    "open": json_res["o"][i],
                    "high": json_res["h"][i],
                    "low": json_res["l"][i],
                    "close": json_res["c"][i],
                    "volume": json_res["v"][i],
                }
            )

        df = pd.DataFrame(result_list)
        df.set_index("datetime", inplace=True)
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M", exact=False)
        return df

    def get_news(self, symbol: str, start_date: datetime, end_date: datetime):
        pass

    def get_splits(self, symbol: str, start_date: str, end_date: str):
        pass

    def get_market_news(self):
        pass

    def get_candles(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        time_frame: dict,
        force_provider_fetch: bool = False,
        store_fetched_data: bool = False,
    ):
        tf = time_frame["multiplier"]
        tf += time_frame["timeframe"]

        if time_frame["timeframe"] == "Min":
            df = self.get_minute_candles(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_provider_fetch=force_provider_fetch,
                store_fetched_data=store_fetched_data,
            )
        elif time_frame["timeframe"] == "Day":
            df = self.get_daily_candles(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                force_provider_fetch=force_provider_fetch,
                store_fetched_data=store_fetched_data,
            )
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

    def get_daily_candles(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        force_provider_fetch: bool = False,
        store_fetched_data: bool = False,
    ):
        pass

    def get_minute_candles(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        force_provider_fetch: bool = False,
        store_fetched_data: bool = False,
    ):
        # Finnhub uses UNIX time-stamps to operate with time ranges so we need to convert to datetime
        start_date = MarketDataUtils.from_string_to_datetime(start_date)
        end_date = MarketDataUtils.from_string_to_datetime(end_date)
        end_date = end_date + timedelta(days=1)

        if force_provider_fetch is False:
            log.debug(
                "Loading candles from db for {} time between {} {}".format(
                    symbol, start_date, end_date
                )
            )
            db = DBManager()
            df = db.minute_candles_to_dataframe(symbol, start_date, end_date)
            if MarketDataUtils.check_candles_in_timeframe(df, start_date, end_date):
                db.close()
                log.debug("Successfully fetched {} candles ".format(df.shape[0]))
                df["ny_datetime"] = df.index - pd.DateOffset(hours=4)
                return df
            else:
                log.warning("No candles available in db, fetching from data provider")

        log.debug("Fetching minute candles on " + self.get_provider_name() + " api")
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
            "adjusted": "true",
        }

        res = self.get(endpoint, params)

        try:
            json_res = res.json()
        except Exception as e:
            log.error("Response not in json format " + res.text)
            log.error(e)
            return None

        df = self._transform_to_dataframe(json_res, native_tz=True)
        df.drop(pd.Timestamp(end_date_filter), inplace=True, errors="ignore")

        if store_fetched_data is True:
            try:
                db = DBManager()
                db.dataframe_to_minute_candles(symbol, df)
                db.close()
            except Exception as e:
                log.error("Failed to store data in db: {}".format(e))

        return df

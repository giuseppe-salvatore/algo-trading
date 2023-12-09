import pandas as pd
import requests as req
import pandas_market_calendars as mcal

from datetime import datetime
from datetime import timedelta

from lib.util.logger import log


class MarketDataProvider:
    def __init__(self):
        self.base_url = None
        self.provider_name = None
        self.provider_url = None
        self.nyse = None

    def set_provider_name(self, name: str):
        self.provider_name = name

    def get_provider_name(self):
        return self.provider_name

    def set_provider_url(self, url: str):
        self.provider_url = url

    def get_provider_url(self):
        return self.provider_url

    def set_base_url(self, url: str):
        self.base_url = url

    def get_base_url(self):
        return self.base_url

    def datetime_to_string(self, dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    def append_params(self, url: str, params: dict = None):
        key = self.get_key_name()
        value = self.get_key_value()

        if key is None:
            log.error("Key is None")
        if value is None:
            log.error("Value for key {} is none".format(key))
        url += "?" + key + "=" + value
        if params is not None:
            for key in params:
                url += "&" + key + "=" + str(params[key])
        return url

    def get(self, endpoint: str, params: dict = None):
        url = self.get_base_url() + endpoint
        url = self.append_params(url, params)
        print("Sending GET request: " + url)
        resp = req.get(url)
        if resp.status_code != 200:
            raise Exception(
                "Error performing GET request to url: {} \n \
                            Status code: {} \n \
                            Content : {}".format(
                    url, resp.status_code, resp.text
                )
            )
        return resp

    def get_key_name(self):
        pass

    def get_key_value(self):
        pass

    def get_minute_candles(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        force_provider_fetch: bool = False,
        store_fetched_data: bool = False,
    ):
        pass

    def _fetch_minute_candles(
        self, symbol: str, start_date: datetime, end_date: datetime
    ):
        pass

    def get_day_candles(self, symbol: str, start_date: datetime, end_date: datetime):
        pass

    def get_news(self):
        log.error(
            "The get_news() API is not supported or not free on " + self.provider_name
        )

    def get_supported_symbols(self):
        log.error(
            "The get_supported_symbols() API is not supported or not free on {}".format(
                self.provider_name
            )
        )

    def get_symbol_details(self, symbol: str):
        log.error(
            "The get_symbol_details() API is not supported or not free on {}".format(
                self.provider_name
            )
        )

    def get_financials(self, symbol: str):
        log.error(
            "The get_financials() API is not supported or not free on {}".format(
                self.provider_name
            )
        )


class MarketDataUtils:
    @staticmethod
    def from_string_to_datetime(date):
        if isinstance(date, str):
            return datetime.strptime(date, "%Y-%m-%d")
        return date

    @staticmethod
    def is_market_day(day, exchange: str = "NYSE") -> bool:
        exchange = mcal.get_calendar(exchange)
        day = MarketDataUtils.from_string_to_datetime(day)

        start_date = day - timedelta(days=2)
        end_date = day + timedelta(days=2)

        nsye_dates = exchange.schedule(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        log.debug("{0} < day = {1} < {2}".format(start_date, day, end_date))

        log.debug(
            "Market days in a range of +/- 2 days: {}".format(nsye_dates.index.date)
        )

        return True if day.date() in nsye_dates.index.date else False

    @staticmethod
    def get_market_days_in_range(start_date, end_date, exchange: str = "NYSE") -> int:
        return MarketDataUtils.get_market_days_and_time_in_range(
            start_date, end_date, exchange
        ).index.date

    @staticmethod
    def get_market_days_and_time_in_range(
        start_date, end_date, exchange: str = "NYSE"
    ) -> pd.DataFrame:
        exchange = mcal.get_calendar(exchange)

        start_date = MarketDataUtils.from_string_to_datetime(start_date)
        end_date = MarketDataUtils.from_string_to_datetime(end_date)

        exchange_dates = exchange.schedule(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        exchange_dates["market_open"] = exchange_dates["market_open"].dt.tz_convert(
            "America/New_York"
        )
        exchange_dates["market_close"] = exchange_dates["market_close"].dt.tz_convert(
            "America/New_York"
        )

        return exchange_dates

    @staticmethod
    def get_market_open_time_on_date(exchange_dataframe, date):
        open_close = exchange_dataframe.loc[str(date), :]
        return open_close.loc["market_open"]

    @staticmethod
    def get_market_close_time_on_date(exchange_dataframe, date):
        open_close = exchange_dataframe.loc[str(date), :]
        return open_close.loc["market_close"]

    @staticmethod
    def get_market_open_time(start_date):
        return "9:30", "15:59"

    @staticmethod
    def get_market_open_time_as_datetime(start_date):
        if type(start_date) is str:
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        yr = start_date.year
        mnt = start_date.month
        day = start_date.day
        return datetime(yr, mnt, day, 9, 30), datetime(yr, mnt, day, 16, 00)

    @staticmethod
    def check_candles_in_timeframe(
        df: pd.DataFrame,
        start_date: datetime,
        end_date: datetime,
        expected_candles_per_day: int = 385,
    ):
        if df is None:
            raise ValueError("Dataframe is None")

        if end_date < start_date:
            raise ValueError("Start date should be earlier than stop date")

        delta_days = end_date - start_date

        if delta_days.days == 0:
            raise ValueError("There should be at least one day delta in time frame")

        tmp_start = datetime(start_date.year, start_date.month, start_date.day, 0, 0)
        tmp_end = None

        exchange = mcal.get_calendar("NYSE")

        exchange_dates = exchange.schedule(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

        log.debug("Days in range: {}".format(delta_days.days))
        log.debug("Trading days in range: {}".format(len(exchange_dates.index.date)))

        print(exchange_dates.index.date)
        print("--------------------------")

        for i in range(delta_days.days):
            # We check if the day we are interested is actually in a market day
            if tmp_start.date() in exchange_dates.index.date:

                log.debug("Checking candles in date {}".format(tmp_start.date()))

                # Creating a mask to filter between start date and end date, considering
                # tmp end is always tmp start plus one day and that start date will start
                # from same date as passed by parameter but forcing time at 00:00
                tmp_end = tmp_start + timedelta(days=1)
                filtered_df = df.loc[tmp_start:tmp_end]
                filtered_by_time = filtered_df.between_time("9:30", "16:00")

                expected_min_candles = 200
                if len(filtered_by_time.index) < expected_min_candles:
                    log.warning(
                        "Candles for {} -> {} are {}, expected {}".format(
                            tmp_start,
                            tmp_end,
                            len(filtered_by_time.index),
                            expected_min_candles,
                        )
                    )
                    return False
                tmp_start = tmp_end
            else:
                tmp_end = tmp_start + timedelta(days=1)
                tmp_start = tmp_end

        return True

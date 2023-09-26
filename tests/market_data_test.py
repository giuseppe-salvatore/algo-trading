import unittest
import pandas as pd
from datetime import datetime

# Project specific imports from lib
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.provider_utils import MarketDataProviderUtils
from lib.market_data_provider.market_data_provider import MarketDataUtils


class FinnhubMarketDataProviderTest(unittest.TestCase):

    def test_data_provider_creation(self):
        provider_name = "Finnhub"
        log.debug("Initialising {} data provider".format(provider_name))
        provider = MarketDataProviderUtils.get_provider(provider_name)
        self.assertTrue(provider is not None)
        self.assertEqual(provider.get_provider_name(), provider_name)

    def test_get_minute_candles(self):
        provider = MarketDataProviderUtils.get_provider("Finnhub")
        df = provider.get_minute_candles(
            symbol="TSLA",
            start_date=
            "2023-08-07",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            end_date=
            "2023-08-19",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            force_provider_fetch=True,
            store_fetched_data=False)
        self.assertTrue(len(df.index) > 100)

    def test_minute_candle_content_on_single_day(self):
        provider = MarketDataProviderUtils.get_provider("Finnhub")
        df = provider.get_minute_candles(
            symbol="TSLA",
            start_date=
            "2023-08-07",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            end_date=
            "2023-08-08",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            force_provider_fetch=True,
            store_fetched_data=False)
        self.assertTrue(len(df.index) > 100)

    def test_minute_candle_range(self):
        provider = MarketDataProviderUtils.get_provider("Finnhub")
        df = provider.get_minute_candles(
            symbol="TSLA",
            start_date=
            "2023-08-07",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            end_date=
            "2023-08-09",  # TODO: replace me with a dynamic version of data otherwise will fail in future
            force_provider_fetch=True,
            store_fetched_data=False)
        indexes = df.index.values
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-06") not in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-10") not in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-11") not in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-12") not in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-07 15:00") in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-08 15:00") in indexes)
        # TODO: these should be generated based on the above
        self.assertTrue(pd.to_datetime("2023-08-09 15:00") in indexes)


class PolygonMarketDataProviderTest(unittest.TestCase):

    def test_data_provider_creation(self):
        provider_name = "Polygon"
        log.debug("Initialising {} data provider".format(provider_name))
        provider = MarketDataProviderUtils.get_provider(provider_name)
        self.assertTrue(provider is not None)
        self.assertEqual(provider.get_provider_name(), provider_name)


class GenericFailureMarketDataProviderTest(unittest.TestCase):

    def test_exception_is_raised(self):
        self.assertRaises(ValueError, MarketDataProviderUtils.get_provider,
                          "unknown")

    def test_minute_candles_checker_null_dataframe(self):
        self.assertRaises(ValueError,
                          MarketDataUtils.check_candles_in_timeframe, None,
                          datetime(2023, 8, 7), datetime(2023, 8, 8))

    def test_minute_candles_checker_reverse_dates(self):
        self.assertRaises(ValueError,
                          MarketDataUtils.check_candles_in_timeframe, 1,
                          datetime(2020, 10, 7), datetime(2020, 10, 5))

    def test_minute_candles_checker_same_date(self):
        self.assertRaises(ValueError,
                          MarketDataUtils.check_candles_in_timeframe, 1,
                          datetime(2020, 10, 5), datetime(2020, 10, 5))

    def test_minute_candles_checker_multiple_days(self):
        db = DBManager()
        df = db.minute_candles_to_dataframe('AAPL', datetime(2020, 9, 7),
                                            datetime(2020, 9, 9))
        res = MarketDataUtils.check_candles_in_timeframe(
            df, datetime(2020, 9, 6), datetime(2020, 9, 10))
        self.assertTrue(res)

    def test_date_is_maket_day(self):
        self.assertTrue(MarketDataUtils.is_market_day("2020-05-29"))

    def test_date_is_not_maket_day(self):
        self.assertTrue(MarketDataUtils.is_market_day("2020-05-26"))

    def test_market_dates_in_range(self):
        market_dates = MarketDataUtils.get_market_days_in_range(
            "2020-10-05", "2020-10-09")
        log.debug(market_dates)
        self.assertEqual(len(market_dates), 5)

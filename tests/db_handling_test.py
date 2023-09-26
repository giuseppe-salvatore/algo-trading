import unittest
from datetime import datetime
from dateutil.relativedelta import relativedelta, MO, FR

# Project specific imports
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.market_data_provider import MarketDataUtils
from lib.market_data_provider.provider_utils import MarketDataProviderUtils


class MarketDataDatabaseTest(unittest.TestCase):

    def test_store_market_data_in_db(self):

        db = DBManager()
        fh = MarketDataProviderUtils.get_provider("Finnhub")
        db.delete_rows_from("minute_bars", "symbol='TSLA'")
        dataframe = fh.get_minute_candles(
            'TSLA',
            datetime(
                2023, 8,
                9),  # TODO: replace this with a dynamic version of the data
            datetime(
                2023, 8,
                20),  # TODO: replace this with a dynamic version of the data
            force_provider_fetch=True,
            store_fetched_data=False)
        log.debug("\n{}".format(dataframe))

        db.dataframe_to_minute_candles('TSLA', dataframe)
        db.delete_rows_from("minute_bars", "symbol='TSLA'")
        db.close()

    # def test_store_market_data_in_db_with_diffs(self):

    #     db = DBManager()
    #     fh = MarketDataProviderUtils.get_provider("Finnhub")

    #     db.delete_rows_from("minute_bars", "symbol='TSLA'")
    #     start_date1 = datetime(2020, 10, 5)
    #     end_date1 = datetime(2020, 10, 7)
    #     dataframe1 = fh.get_minute_candles(
    #         'TSLA',
    #         start_date1,
    #         end_date1,
    #         force_provider_fetch=True,
    #         store_fetched_data=True)
    #     res = MarketDataUtils.check_candles_in_timeframe(
    #         dataframe1,
    #         start_date1,
    #         end_date1)
    #     self.assertTrue(res)
    #     print(dataframe1)

    #     start_date2 = datetime(2020, 10, 6)
    #     end_date2 = datetime(2020, 10, 9)
    #     dataframe2 = fh.get_minute_candles(
    #         'TSLA',
    #         start_date2,
    #         end_date2,
    #         store_fetched_data=True)
    #     res = MarketDataUtils.check_candles_in_timeframe(
    #         dataframe2,
    #         start_date2,
    #         end_date2)
    #     self.assertTrue(res)
    #     db.close()

    # def test_store_market_data_in_db_with_diffs_3(self):

    #     db = DBManager()
    #     db.delete_rows_from("minute_bars", "symbol='TSLA'")

    #     fh = MarketDataProviderUtils.get_provider("Finnhub")
    #     start_date1 = datetime(2020, 10, 6)
    #     end_date1 = datetime(2020, 10, 9)
    #     dataframe1 = fh.get_minute_candles(
    #         'TSLA',
    #         start_date1,
    #         end_date1,
    #         force_provider_fetch=True,
    #         store_fetched_data=True)
    #     res = MarketDataUtils.check_candles_in_timeframe(
    #         dataframe1,
    #         start_date1,
    #         end_date1)
    #     self.assertTrue(res)
    #     print(dataframe1)

    #     start_date2 = datetime(2020, 10, 5)
    #     end_date2 = datetime(2020, 10, 7)
    #     dataframe2 = fh.get_minute_candles(
    #         'TSLA',
    #         start_date2,
    #         end_date2,
    #         force_provider_fetch=True,
    #         store_fetched_data=False)
    #     res = MarketDataUtils.check_candles_in_timeframe(
    #         dataframe2,
    #         start_date2,
    #         end_date2)
    #     db.dataframe_to_minute_candles('TSLA', dataframe2)
    #     self.assertTrue(res)
    #     db.close()

    # def test_load_market_data_from_db_date_as_datetime(self):

    #     db = DBManager()
    #     start_date = datetime(2020, 10, 6)
    #     end_date = datetime(2020, 10, 10)
    #     fh = MarketDataProviderUtils.get_provider("Finnhub")
    #     db.delete_rows_from("minute_bars", "symbol='TSLA'")
    #     fh.get_minute_candles(
    #         'TSLA',
    #         datetime(2020, 10, 6),
    #         datetime(2020, 10, 10),
    #         force_provider_fetch=True,
    #         store_fetched_data=True)
    #     df = db.minute_candles_to_dataframe('TSLA', start_date, end_date)
    #     db.close()
    #     log.debug(df)
    #     log.debug(df.shape)

    #     self.assertTrue(df.shape[0] > 390)

    # def test_store_market_data_in_db_with_diffs_2(self):

    #     db = DBManager()
    #     db.delete_rows_from("minute_bars", "symbol='TSLA'")

    #     df_from_db = db.minute_candles_to_dataframe(
    #         "TSLA",
    #         datetime(2020, 10, 6),
    #         datetime(2020, 10, 9)
    #     )
    #     self.assertTrue(len(df_from_db) == 0)

    #     fh = MarketDataProviderUtils.get_provider("Finnhub")
    #     start_date1 = datetime(2020, 10, 6)
    #     end_date1 = datetime(2020, 10, 9)
    #     dataframe1 = fh.get_minute_candles(
    #         'TSLA',
    #         start_date1,
    #         end_date1,
    #         force_provider_fetch=True,
    #         store_fetched_data=True)

    #     df_from_db = db.minute_candles_to_dataframe(
    #         "TSLA",
    #         datetime(2020, 10, 6),
    #         datetime(2020, 10, 9)
    #     )

    #     log.info("Pulled data = {}".format(len(dataframe1)))
    #     log.info("Database data = {}".format(len(df_from_db)))
    #     self.assertTrue(len(dataframe1) == len(df_from_db))

    #     log.debug("\n{}".format(dataframe1))

    # def test_store_market_data_in_db_in_long_range(self):

    #     db = DBManager()
    #     fh = MarketDataProviderUtils.get_provider("Finnhub")
    #     db.delete_rows_from("minute_bars", "symbol='AAPL'")
    #     start = datetime(2020, 8, 1)
    #     end = datetime(2020, 9, 30)
    #     dataframe = fh.get_minute_candles(
    #         'AAPL',
    #         start,
    #         end,
    #         force_provider_fetch=True,
    #         store_fetched_data=True)
    #     log.debug("\n{}".format(dataframe))

    #     dataframe = fh.get_minute_candles(
    #         'AAPL',
    #         datetime(2020, 7, 15),
    #         datetime(2020, 8, 15),
    #         force_provider_fetch=False,
    #         store_fetched_data=True)
    #     res = MarketDataUtils.check_candles_in_timeframe(
    #         dataframe,
    #         datetime(2020, 7, 15),
    #         datetime(2020, 8, 15))
    #     self.assertTrue(res)

    #     # db.dataframe_to_minute_candles('AAPL', dataframe)
    #     db.close()

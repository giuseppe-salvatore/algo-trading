import unittest
from datetime import datetime

# Project specific imports
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.finnhub import FinnhubDataProvider


class MarketDataDatabaseTest(unittest.TestCase):

    def test_store_market_data_in_db(self):

        db = DBManager("tests/data/test_data.db")
        fh = FinnhubDataProvider()
        dataframe = fh.get_minute_candles('TSLA', datetime(2020, 10, 6), datetime(2020, 10, 9))

        db.delete_rows_from("minute_bars", "symbol='TEST'")
        db.dataframe_to_minute_candles('TEST', dataframe)

        db.close()

    def test_load_market_data_from_db_date_as_datetime(self):

        db = DBManager("tests/data/test_data.db")
        start_date = datetime(2020, 10, 6)
        end_date = datetime(2020, 10, 9)
        print(start_date)
        print(type(start_date))
        df = db.minute_candles_to_dataframe('TEST', start_date, end_date)
        db.close()
        log.debug(df)
        log.debug(df.shape)

        self.assertTrue(df.shape[0] > 390)


if __name__ == '__main__':
    unittest.main()

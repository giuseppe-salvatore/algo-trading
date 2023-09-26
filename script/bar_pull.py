# import sqlite3
# import datetime
# import pandas as pd
# import lib.util.logger as log
# import lib.db.queries as db_queries
# import pandas_market_calendars as mcal

# from sqlite3 import Error
# from lib.trading.alpaca import AlpacaTrading
import time
from datetime import datetime
from lib.util.logger import log
from lib.db.manager import DBManager
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

if __name__ == "__main__":

    provider = MarketDataProviderUtils.get_provider("Finnhub")
    db = DBManager()
    tuple_list = db.get_filtered_watchlist_sortedby_marketcap()
    watchlist = ["WORK"]
    # for elem in tuple_list:
    #     watchlist.append(elem[0])

    dates = []

    # start = datetime(2019, 12, 30)
    # end = datetime(2020, 1, 17)
    # dates.append([start, end])

    # start = datetime(2020, 1, 20)
    # end = datetime(2020, 2, 7)
    # dates.append([start, end])

    # start = datetime(2020, 2, 10)
    # end = datetime(2020, 2, 28)
    # dates.append([start, end])

    # start = datetime(2020, 3, 2)
    # end = datetime(2020, 3, 20)
    # dates.append([start, end])

    # start = datetime(2020, 3, 23)
    # end = datetime(2020, 4, 10)
    # dates.append([start, end])

    # start = datetime(2020, 4, 13)
    # end = datetime(2020, 5, 1)
    # dates.append([start, end])

    # start = datetime(2020, 5, 4)
    # end = datetime(2020, 5, 22)
    # dates.append([start, end])

    # start = datetime(2020, 5, 25)
    # end = datetime(2020, 6, 12)
    # dates.append([start, end])

    # start = datetime(2020, 6, 15)
    # end = datetime(2020, 7, 3)
    # dates.append([start, end])

    # start = datetime(2020, 7, 6)
    # end = datetime(2020, 7, 24)
    # dates.append([start, end])

    # start = datetime(2020, 7, 27)
    # end = datetime(2020, 8, 7)
    # dates.append([start, end])

    # start = datetime(2020, 8, 10)
    # end = datetime(2020, 8, 28)
    # dates.append([start, end])

    # start = datetime(2020, 8, 31)
    # end = datetime(2020, 9, 18)
    # dates.append([start, end])

    # start = datetime(2020, 9, 21)
    # end = datetime(2020, 10, 9)
    # dates.append([start, end])

    # start = datetime(2020, 10, 12)
    # end = datetime(2020, 10, 30)
    # dates.append([start, end])

    start = datetime(2020, 11, 2)
    end = datetime(2020, 11, 20)
    dates.append([start, end])

    start = datetime(2020, 11, 23)
    end = datetime(2020, 12, 11)
    dates.append([start, end])

    black_list = ["AMTD", "NBL", "ETFC"]

    # my_static_stock = [
    #     "WORK", "UBER", "SPOT", "SPCE", "PTON", "NIO", "MRNA", "BYND", "BRK.B",
    #     "ARKG", "HEXO", "ABT", "ANET", "APA", "AVGO", "CCL", "CMCSA", "CPE", "CVX", "CSCO",
    #     "EPAM", "EXC", "IBB", "LMT", "MPC", "NVTA", "OXY", "ROKU", "SNDX", "SPY", "SPGI",
    #     "TM", "TMUS", "TOT", "TTM", "UNH", "XBI", "XOM", "ZM"
    # ]

    # for elem in my_static_stock:
    #     if elem not in watchlist:
    #         watchlist.append(elem)

    # log.info("There are {} stocks in your watchlist".format(len(watchlist)))

    # for elem in black_list:
    #     watchlist.remove(elem)

    log.info("There are {} stocks in your watchlist".format(len(watchlist)))

    for range_date in dates:
        start = range_date[0]
        end = range_date[1]
        log.info("Fetching from {} to {}".format(start, end))
        for symbol in watchlist:
            if symbol in black_list:
                log.warning(
                    "Skipping symbol as it's in the blacklist: {}".format(
                        symbol))
                continue
            try:
                dataframe = provider.get_minute_candles(
                    symbol,
                    start,
                    end,
                    force_provider_fetch=True,
                    store_fetched_data=True)
            except Exception as e:
                log.critical("Failed to fetch data for " + symbol)
                log.critical(e)
            time.sleep(2)

    # for symbol in watchlist:
    #     # if skip:
    #     #     print("Skipping: " + symbol)
    #     #     if symbol == skip_until:
    #     #         skip = False
    #     #     continue
    #     if symbol in black_list:
    #         log.warning("Skipping {} as it's in the blacklist".format(symbol))
    #         continue
    #     try:
    #         dataframe = provider.get_minute_candles(
    #             symbol,
    #             start,
    #             end,
    #             force_provider_fetch=True,
    #             store_fetched_data=True)
    #     except Exception as e:
    #         log.critical("Failed to fetch data for " + symbol)
    #         log.critical(e)
    #     time.sleep(2)

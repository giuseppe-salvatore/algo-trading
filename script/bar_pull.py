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
    watchlist = ["AAPL", "MSFT", "GOOGL",  "SPY", ]
    # for elem in tuple_list:
    #     watchlist.append(elem[0])

    dates = []

    # start = datetime(2019, 11, 10)
    # end = datetime(2019, 12, 1)
    # dates.append([start, end])

    # start = datetime(2019, 12, 2)
    # end = datetime(2020, 2, 1)
    # dates.append([start, end])

    # start = datetime(2020, 2, 2)
    # end = datetime(2020, 4, 1)
    # dates.append([start, end])

    # start = datetime(2020, 4, 2)
    # end = datetime(2020, 6, 1)
    # dates.append([start, end])

    # start = datetime(2020, 6, 2)
    # end = datetime(2020, 8, 1)
    # dates.append([start, end])

    start = datetime(2020, 10, 20)
    end = datetime(2020, 10, 31)
    dates.append([start, end])

    # black_list = ["AMTD", "NBL", "ETFC"]

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
        log.info("Fetching from {} to {}".format(
            start,
            end
        ))
        for symbol in watchlist:
            # if symbol in watchlist:
            #     log.warning("Skipping symbol as it's in the watchlist already: {}".format(symbol))
            #     continue
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

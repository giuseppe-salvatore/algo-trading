"""
You can run the script with python -m script.alpaca_market_data_pull on the 1st of each month
If no argument is passed it is assumed to go and fetch the data only for the previous month
so it's good to run it on the first of each month to pull the previous month data
"""

import sys
import time
import multiprocessing as mp
from datetime import timedelta

from conf.secret import ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET
from lib.util.logger import log

from datetime import datetime
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient

months = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]


def time_diff(start_time: datetime, end_time: datetime) -> str:
    return str(end_time - start_time).split('.', 2)[0]


def to_userfriendly_str(time: str) -> str:
    tokens = time.split(':')
    final_str = ""
    if int(tokens[0]) > 0:
        final_str += str(int(tokens[0]))
        final_str += " hours"

    if int(tokens[1]) > 0:
        final_str += " "
        final_str += str(int(tokens[1]))
        final_str += " minutes"

    if (int(tokens[0]) > 0 or int(tokens[1]) > 0) and int(tokens[2]) > 0:
        final_str += " and "
        final_str += str(int(tokens[2]))
        final_str += " seconds"
    else:
        final_str += " "
        final_str += str(int(tokens[2]))
        final_str += " seconds"

    return final_str


def convert_to_ny_tz_string(utc_tz):
    return str(utc_tz.tz_convert(tz='America/New_York'))[:19]


def print_sql_transaction(df, symbol):

    dest_str = ""
    for index, elem in df.iterrows():
        dest_str += "(\"{}\",\"{}\",{:3.2f},{:3.2f},{:3.2f},{:3.2f},{:.0f}),\n".format(
            symbol, convert_to_ny_tz_string(index[1]), elem["open"], elem["close"], elem["high"], elem["low"], elem["volume"])

    return dest_str


def get_start_end_dates():

    dates = []

    # for year in [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]:
    #     for month in range(1, 13):
    #         start = datetime(year, month, 1)
    #         if month + 1 == 13:
    #             end = datetime(year + 1, 1, 1)
    #         else:
    #             end = datetime(year, month + 1, 1)
    #         dates.append((start, end))
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    if current_month == 1:
        # on january we need to go back previous year
        # for the start date
        start = datetime(current_year - 1, 12, 1)
        end = datetime(current_year, current_month, 1)
    else:
        start = datetime(current_year, current_month - 1, 1)
        end = datetime(current_year, current_month, 1)

    dates.append((start, end))

    # month by month
    # for year in [2023]:
    #     for month in range(7, 8):
    #         start = datetime(year, month, 1)
    #         if month + 1 == 13:
    #             end = datetime(year + 1, 1, 1)
    #         else:
    #             end = datetime(year, month + 1, 1)
    #         dates.append((start, end))

    return dates


def pull_stock_data_for_symbol(symbol, target_month, months_to_process):
    # start is included end is excluded so if you only want bars for 2023-03-14
    # then set the following
    # start=datetime.strptime("2023-03-14", '%Y-%m-%d'),
    # end=datetime.strptime("2023-03-15", '%Y-%m-%d')

    destfile = open(".tmp/{}.sql.{}-2023.sql".format(symbol, months[target_month]), "w")

    dest_str = "BEGIN TRANSACTION;\n"
    dest_str += "INSERT INTO minute_bars (symbol,time,open,close,high,low,volume) VALUES\n"

    body = ""

    # Every start and end date corresponds to a month
    for date in get_start_end_dates():

        log.info("Processing {} from {} to {}".format(symbol, date[0], date[1]))

        try:
            # keys required for stockdata data
            client = StockHistoricalDataClient(ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET)

            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Minute,
                start=date[0],
                end=date[1]
            )

            bars = client.get_stock_bars(request_params)

            res = print_sql_transaction(bars.df, symbol)
            body += res
            dest_str += res

        except Exception as e:
            log.warning(e)

        dest_str = ";".join(dest_str.rsplit(",", 1))
        dest_str += "COMMIT;\n"
        destfile.write(dest_str)
        destfile.close()

        # sys.stdout.write("DONE in {}\n".format(to_userfriendly_str(
        #     time_diff(
        #         start_proc,
        #         datetime.utcnow()
        #     ))))
        # sys.stdout.flush()

        #print("Bar count for {} = {}".format(symbol, count))
    return body


if __name__ == '__main__':

    max_processes = mp.cpu_count()
    log.info("Available parallel execution threads: {}".format(max_processes))

    start = time.time()
    log.info("Initialising a multiprocess pool with {} parallel processes".format(max_processes))
    pool = mp.Pool(max_processes)
    res = []

    target_month = datetime.now().month - 2
    log.info("Target month(s) is {}".format(months[target_month]))

    symbols = []
    # for sym in open("stocklists/in_sqlite3_finnhub.py", "r"):
    for sym in open("stocklists/master-watchlist-reduced.py", "r"):
        sym = sym.replace("\n", "")
        if sym not in symbols:
            symbols.append(sym)

    print(symbols)
    body_str = "BEGIN TRANSACTION;\n"
    body_str += "INSERT INTO minute_bars (symbol,time,open,close,high,low,volume) VALUES\n"

    for sym in symbols:
        res.append(pool.apply_async(pull_stock_data_for_symbol, args=(sym, target_month, 1)))

    for r in res:
        body_str += r.get()

    pool.close()
    pool.join()

    destfile = open(".tmp/{}.sql.{}-2023.sql".format("ALL_SYMBOLS", months[target_month]), "w")

    body_str = ";".join(body_str.rsplit(",", 1))
    body_str += "COMMIT;\n"
    destfile.write(body_str)
    destfile.close()

    end = time.time()

    log.info("Total execution time to process {} symbols was {} minutes {} seconds".format(
        len(symbols), int((end - start)/60), int((end - start) % 60)))

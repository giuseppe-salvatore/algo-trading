"""
You can run the script with python -m script.alpaca_market_data_pull on the 1st of each month
If no argument is passed it is assumed to go and fetch the data only for the previous month
so it's good to run it on the first of each month to pull the previous month data
"""
import os
import time
import multiprocessing as mp
from datetime import timedelta

from conf.secret import ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET
from lib.util.logger import log

from datetime import datetime
from alpaca.data.timeframe import TimeFrame
from alpaca.data.requests import StockBarsRequest
from alpaca.data.historical import StockHistoricalDataClient


FIX_MODE = False

months = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


# data_to_fix = {
# "AA": [ 2016, 10],
# "AMD": [ 2020, 9],
# "APA": [ 2022, 1],
# "AVGO": [ 2016, 2],
# "BK": [ 2023, 1],
# "CHD": [ 2016, 10],
# "CSCO": [ 2020, 6],
# "CTSH": [ 2019, 5],
# "FE": [ 2016, 8],
# "FTI": [ 2017, 1],
# "HBAN": [ 2019, 8],
# "HST": [ 2017, 9],
# "INTC": [ 2022, 9],
# "KEY": [ 2019, 10],
# "LRCX": [ 2020, 6],
# "LUV": [ 2019, 9],
# "MET": [ 2021, 5],
# "MT": [ 2017, 5],
# "MTG": [ 2020, 1],
# "MUR": [ 2018, 7],
# "NKE": [ 2018, 6],
# "ON": [ 2023, 3],
# "QCOM": [ 2023, 1],
# "SLV": [ 2021, 2],
# "STX": [ 2022, 8],
# "TPR": [ 2017, 3],
# "UAL": [ 2021, 7],
# "VALE": [ 2016, 3],
# "VZ": [ 2019, 4],
# "XLU": [ 2021, 6],
# }

data_to_fix = {
    # "AA": [ 2016, 10],
    # "FTI": [ 2017, 1],
    "KEY": [2019, 10],
    "MUR": [2018, 7],
    "MT": [2017, 5],
}


def time_diff(start_time: datetime, end_time: datetime) -> str:
    return str(end_time - start_time).split(".", 2)[0]


def to_userfriendly_str(time: str) -> str:
    tokens = time.split(":")
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
    return str(utc_tz.tz_convert(tz="America/New_York"))[:19]


def print_sql_transaction(df, symbol):
    dest_str = ""
    for index, elem in df.iterrows():
        dest_str += '("{}","{}",{:3.2f},{:3.2f},{:3.2f},{:3.2f},{:.0f}),\n'.format(
            symbol,
            convert_to_ny_tz_string(index[1]),
            elem["open"],
            elem["close"],
            elem["high"],
            elem["low"],
            elem["volume"],
        )

    return dest_str


def get_date_str(date: datetime) -> str:
    if date is None:
        return str(datetime.now())[:7]
    else:
        return str(date)[:7]


def get_start_end_date_for_symbol(sym):
    dates = []

    start_year = data_to_fix[sym][0]
    start_month = data_to_fix[sym][1]
    days_before = 10
    days_after = 10

    # The start date is the year, month and the first day of the month
    # unless days_before > 0, in which case we go back days_before days
    start = datetime(start_year, start_month, 1)
    end = start + timedelta(days=31)

    start = start - timedelta(days=days_before)
    end = end + timedelta(days=days_after)

    dates.append((start, end))

    return dates


def get_start_end_dates():
    dates = []

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


def pull_stock_data_for_symbol(symbol, target_month, target_year, months_to_process):
    # start is included end is excluded so if you only want bars for 2023-03-14
    # then set the following
    # start=datetime.strptime("2023-03-14", '%Y-%m-%d'),
    # end=datetime.strptime("2023-03-15", '%Y-%m-%d')

    start = time.time()

    dest_file = open(
        "data/alpaca/sql/{}-{}.sql".format(
            symbol, get_date_str(datetime(target_year, target_month, 1))
        ),
        "w",
    )

    dest_str = "BEGIN TRANSACTION;\n"
    dest_str += (
        "INSERT INTO minute_bars (symbol,time,open,close,high,low,volume) VALUES\n"
    )

    body = ""

    dates = None
    if FIX_MODE is True:
        dates = get_start_end_date_for_symbol(symbol)
    else:
        dates = get_start_end_dates()

    # Every start and end date corresponds to a month
    for date in dates:
        success = False
        while success != True:
            try:
                # keys required for stock data data
                client = StockHistoricalDataClient(
                    ALPACA_LIVE_API_KEY, ALPACA_LIVE_SECRET
                )

                request_params = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame.Minute,
                    start=date[0],
                    end=date[1],
                )

                bars = client.get_stock_bars(request_params)

                res = print_sql_transaction(bars.df, symbol)
                body += res
                dest_str += res
                success = True

            except Exception as e:
                log.error("Exception processing {}".format(symbol))
                log.error(e)
                log.warning(
                    "We are going too fast, slowing down 5 secs and retrying {}".format(
                        symbol
                    )
                )
                time.sleep(5)

        dest_str = ";".join(dest_str.rsplit(",", 1))
        dest_str += "COMMIT;\n"
        dest_file.write(dest_str)
        dest_file.close()

    end = time.time()
    log.info(
        "Processed {} from {} to {} - ETA: {} seconds".format(
            symbol, date[0], date[1], int(end - start)
        )
    )

    return body


if __name__ == "__main__":
    max_processes = mp.cpu_count()
    max_load = 8
    log.info("Available parallel execution threads: {}".format(max_processes))

    start = time.time()
    log.info(
        "Initializing a multi-process pool with {} parallel processes".format(
            min(mp.cpu_count(), max_load)
        )
    )
    pool = mp.Pool(min(mp.cpu_count(), max_load))
    res = []

    target_month = datetime.now().month - 1
    target_year = datetime.now().year

    if FIX_MODE is False:
        log.info("Target month(s) is {}".format(months[target_month]))
    else:
        log.info("Using FIX_MODE now")

    symbols = []

    if FIX_MODE is False:
        for sym in open("stocklists/master-watchlist-reduced.txt", "r"):
            sym = sym.replace("\n", "")
            if sym not in symbols:
                symbols.append(sym)

    print(symbols)
    body_str = "BEGIN TRANSACTION;\n"
    body_str += (
        "INSERT INTO minute_bars (symbol,time,open,close,high,low,volume) VALUES\n"
    )

    if FIX_MODE is True:
        for sym in data_to_fix.keys():
            # In this case we get the symbol, month and year as a single entity we can use to pass
            res.append(
                pool.apply_async(
                    pull_stock_data_for_symbol,
                    args=(sym, data_to_fix[sym][1], data_to_fix[sym][0], 1),
                )
            )
    else:
        for sym in symbols:
            # In this case we will need to generate the year and month somehow
            res.append(
                pool.apply_async(
                    pull_stock_data_for_symbol, args=(sym, target_month, target_year, 1)
                )
            )

    for r in res:
        body_str += r.get()

    pool.close()
    pool.join()

    dest_file = open(
        "data/alpaca/sql/{}-{}-2023.sql".format(
            "ALL_SYMBOLS", get_date_str(datetime(target_year, target_month, 1))
        ),
        "w",
    )

    body_str = ";".join(body_str.rsplit(",", 1))
    body_str += "COMMIT;\n"
    dest_file.write(body_str)
    dest_file.close()

    end = time.time()

    log.info(
        "Total execution time to process {} symbols was {} minutes {} seconds".format(
            len(symbols), int((end - start) / 60), int((end - start) % 60)
        )
    )

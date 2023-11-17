import sys
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from datetime import timedelta
from lib.db.manager import DBManager
from lib.market_data_provider.market_data_provider import MarketDataUtils


def minute_candle_count(start_time, end_time):
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    return end_minutes - start_minutes + 1


TOTAL_RESULT_HEADER = "{:<8} {:<12} {:<12} {:<12} {:<12} {:<8} {:<12}".format(
    "Symbol", "Start Date", "End Date", "Data length", "Market Days", "Cover", "Missing"
)

TOTAL_RESULT_ROW = "{:<8} {:<12} {:<12} {:<12} {:<12} {:<8} {}\n"

if __name__ == "__main__":
    db = DBManager()

    watchlist = []
    print_separate_weeks = True
    print_candles_below_threshold = 100

    black_list = ["AMTD", "NBL", "ETFC", "CMCSA"]

    with_gapping_data = ["SONY", "SNDX", "LBTYK", "LBTYA", "DISCA", "CMCSA"]

    if len(sys.argv) > 1:
        print("Getting data for ", end="")
        for i in range(1, len(sys.argv)):
            print("{} ".format(sys.argv[i]), end="")
            watchlist.append(sys.argv[i])
        print("")
    else:
        print("No symbol specified, using all available in db")
        print("Fetching all symbols with data ...")
        symbols = db.get_all_symbols()
        print("Done")
        for elem in symbols:
            if elem[0] not in black_list and elem[0] not in with_gapping_data:
                watchlist.append(elem[0])

    result = ""
    result += TOTAL_RESULT_HEADER + "\n"

    # weekdays as a tuple
    weekDays = (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )

    unsorted_by_data_available = dict()
    full_data = dict()
    daily_data_acc = ""
    daily_data_list = []

    for sym in watchlist:
        daily_data = ""
        df = db.get_all_minute_candles_to_dataframe(sym, from_table="minute_bars")
        start_date = df.index[0].date()
        end_date = df.index[-1].date()
        exchange_df = MarketDataUtils.get_market_days_and_time_in_range(
            start_date=start_date, end_date=end_date
        )
        market_dates_in_range = MarketDataUtils.get_market_days_in_range(
            start_date=start_date, end_date=end_date
        )
        print("symbol = {}".format(sym))
        print(
            "    {:<12} {} {} {} {} ".format(
                "day", "date", "open time", "close time", "minute candles"
            )
        )
        prev_day = None
        curr_day = None
        total_expected = 0
        total_actual = 0

        for date in market_dates_in_range:
            open_time = MarketDataUtils.get_merket_open_time_on_date(exchange_df, date)
            close_time = MarketDataUtils.get_merket_close_time_on_date(
                exchange_df, date
            )
            close_time = close_time - timedelta(minutes=1)

            df_filtered = df.loc[
                open_time.tz_localize(None) : close_time.tz_localize(None)
            ]
            curr_day = date.weekday()
            if print_separate_weeks and prev_day is not None and prev_day > curr_day:
                print("")
            expected_candles = minute_candle_count(open_time, close_time)
            actual_candles = len(df_filtered)
            total_expected += expected_candles
            total_actual += actual_candles
            missing = expected_candles - actual_candles
            candles_perc = actual_candles / float(expected_candles) * 100
            if candles_perc <= print_candles_below_threshold:
                perc_str = "{:.2f}%".format(
                    actual_candles / float(expected_candles) * 100
                )
                if actual_candles > 0:
                    daily_data = "    {:<12} {} {} {} {}/{} {:>7} {}".format(
                        weekDays[date.weekday()],
                        date,
                        open_time.time(),
                        close_time.time(),
                        actual_candles,
                        expected_candles,
                        perc_str,
                        missing,
                    )
                    daily_data_acc = daily_data_acc + daily_data + "\n"
                    print(daily_data)

                else:
                    daily_data = "    {:<12} {} {} {} {}/{} {:>7} {}".format(
                        weekDays[date.weekday()],
                        date,
                        open_time.time(),
                        close_time.time(),
                        actual_candles,
                        expected_candles,
                        perc_str,
                        missing,
                    )
                    daily_data_acc = daily_data_acc + daily_data + "\n"
                    print(daily_data)
                daily_data_list.append(daily_data)
            prev_day = curr_day

        total_perc = "{:.2f}%".format(total_actual / float(total_expected) * 100)
        result += TOTAL_RESULT_ROW.format(
            sym,
            str(df.index[0].date()),
            str(df.index[-1].date()),
            str(len(df)),
            str(len(market_dates_in_range)),
            total_perc,
            total_expected - total_actual,
        )

        unsorted_by_data_available[sym] = total_actual / float(total_expected) * 100

        full_data[sym] = {
            "Start Date": df.index[0].date(),
            "End Date": df.index[-1].date(),
            "Data length": len(df),
            "Market Days": len(market_dates_in_range),
            "Data availability": total_perc,
            "Missing": total_expected - total_actual,
        }

    sorted_x = sorted(unsorted_by_data_available.items(), key=lambda kv: kv[1])
    sorted_by_data_available = collections.OrderedDict(sorted_x)

    print(result)

    print(TOTAL_RESULT_HEADER)

    for elem in sorted_by_data_available:
        sys.stdout.write(
            TOTAL_RESULT_ROW.format(
                elem,
                str(full_data[elem]["Start Date"]),
                str(full_data[elem]["End Date"]),
                str(full_data[elem]["Data length"]),
                str(full_data[elem]["Market Days"]),
                full_data[elem]["Data availability"],
                full_data[elem]["Missing"],
            )
        )

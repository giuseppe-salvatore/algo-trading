import os
import re
import sys
import collections
from lib.db.manager import DBManager
from lib.market_data_provider.market_data_provider import MarketDataUtils


def minute_candle_count(start_time, end_time):
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    return end_minutes - start_minutes + 1


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
    result += "{:<8} {:<12} {:<12} {} {}\n".format(
        "Symbol",
        "Start Date",
        "End Date",
        "Data lenght",
        "Market Days")

    # weekdays as a tuple
    weekDays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

    unsorted_by_data_available = dict()
    full_data = dict()

    for sym in watchlist:
        df = db.get_all_minute_candles_to_dataframe(sym, from_table='minute_bars')
        start_date = df.index[0].date()
        end_date = df.index[-1].date()
        exchange_df = MarketDataUtils.get_market_days_and_time_in_range(
            start_date=start_date,
            end_date=end_date)
        market_dates_in_range = MarketDataUtils.get_market_days_in_range(
            start_date=start_date,
            end_date=end_date
        )

        print("    {:<12} {} {} {} {} ".format("day", "date", "open time", "close time", "minute candles"))
        prev_day = None
        curr_day = None
        total_expected = 0
        total_actual = 0
        #df.index = df.index.shift(-5, freq='h')
        for date in market_dates_in_range:
            open_time = MarketDataUtils.get_merket_open_time_on_date(exchange_df, date)
            close_time = MarketDataUtils.get_merket_close_time_on_date(exchange_df, date)
            # open_time, close_time = MarketDataUtils.get_market_open_time_as_datetime(date)

            df_filtered = df.loc[open_time.tz_localize(None): close_time.tz_localize(None)]
            curr_day = date.weekday()
            if print_separate_weeks and prev_day is not None and prev_day > curr_day:
                print("")
            expected_candles = minute_candle_count(open_time, close_time)
            actual_candles = len(df_filtered)
            total_expected += expected_candles
            total_actual += actual_candles
            candles_perc = actual_candles/float(expected_candles)*100
            if candles_perc <= print_candles_below_threshold:
                print("    {:<12} {} {} {} {}/{} {:.2f}%".format(weekDays[date.weekday()], date,
                                                                 open_time.time(), close_time.time(),
                                                                 actual_candles, expected_candles,
                                                                 actual_candles/float(expected_candles)*100))
            prev_day = curr_day

        result += "{:<8} {:<12} {:<12} {:<12} {:<12} {:.2f}%\n".format(
            sym,
            str(df.index[0].date()),
            str(df.index[-1].date()),
            str(len(df)),
            str(len(market_dates_in_range)),
            total_actual/float(total_expected)*100
        )

        unsorted_by_data_available[sym] = total_actual/float(total_expected)*100

        full_data[sym] = {
            "Start Date": df.index[0].date(),
            "End Date": df.index[-1].date(),
            "Data length": len(df),
            "Market Days": len(market_dates_in_range),
            "Data availability": total_actual/float(total_expected)*100
        }

    sorted_x = sorted(unsorted_by_data_available.items(), key=lambda kv: kv[1])
    sorted_by_data_available = collections.OrderedDict(sorted_x)

    print(result)

    print("{:<8} {:<12} {:<12} {} {}".format(
        "Symbol",
        "Start Date",
        "End Date",
        "Data lenght",
        "Market Days"))

    for elem in sorted_by_data_available:
        print("{:<8} {:<12} {:<12} {:<12} {:<12} {:.2f}%".format(
            elem,
            str(full_data[elem]["Start Date"]),
            str(full_data[elem]["End Date"]),
            str(full_data[elem]["Data length"]),
            str(full_data[elem]["Market Days"]),
            full_data[elem]["Data availability"]
        ))


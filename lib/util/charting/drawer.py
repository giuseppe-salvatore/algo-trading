# import os
# import sys
# import numpy as np
import pytz
import collections
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.patches import Rectangle
# import matplotlib.ticker as plticker
# import matplotlib.patches as patches
# from matplotlib.patches import Rectangle
# from matplotlib.dates import DateFormatter
from mplfinance.original_flavor import candlestick_ohlc

from lib.trading.generic import Position
from lib.market_data_provider.market_data_provider import MarketDataUtils

class EquityChart():
    def __init__(self):
        self._title = None
        self._symbol = None
        self._tradeing_session = None
        self._starting_capital = None
        self._fig = None
        self._ax = None

    def draw_all(self, save_pic, print_dates):

        plt.clf()
        profits = {}
        symbols = self.trading_session.get_symbols()
        for symbol in symbols:
            for position in self.trading_session.get_positions(symbol):
                date = position.get_close_datetime()
                profit = position.get_profit()
                if date is None:
                    continue
                if date not in profits:
                    profits[date] = profit
                else:
                    profits[date] += profit

        for elem in profits:
            if elem is None or profits[elem] is None:
                print("Something is None here")
                print("{} {}".format(elem, profits[elem]))
        print("------------------------")

        od = collections.OrderedDict(sorted(profits.items()))

        current_capital = self.starting_capital
        for elem in od:
            current_capital += od[elem]
            od[elem] = current_capital

        file_name = ""

        if print_dates:
            file_name = "TotalEquityWithDates.png"
            df = pd.DataFrame(
                {"equity": od.values(),
                 "dates": od.keys()}
            )
            df.set_index("dates", inplace=True)
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M', exact=False)
        else:
            file_name = "TotalEquityNoDates.png"
            df = pd.DataFrame(
                {"equity": od.values()}
            )

        df["equity"].plot()
        if save_pic:
            plt.savefig(self.result_folder + "/" + file_name)
            plt.close()
        else:
            plt.show()
            plt.close()


class TradeChart():
    def __init__(self):
        self._title = None
        self._symbol = None
        self._indicators = []
        self._market_data = None
        self._tradeing_session = None
        self._fig = None
        self._ax = None

    def add_position(self, position):
        self.positions.append(position)

    def draw_date(self, symbol, date, save_pic):

        md = self.market_data[symbol]
        start_date = datetime(date.year, date.month, date.day, 0, 0)
        market_open, market_close = MarketDataUtils.get_market_open_time_as_datetime(date)
        end_date = datetime(date.year, date.month, date.day, 23, 59)

        md["SMMA 20"] = (md["close"].ewm(span=20, adjust=False).mean() * 2 - 1) / 2
        md["SMMA 50"] = (md["close"].ewm(span=50, adjust=False).mean() * 2 - 1) / 2
        datetime_mask = (md.index >= start_date) & (md.index <= end_date)
        sub_df = md.loc[datetime_mask].between_time("9:30", "16:00")
        # sub_df['close'].between_time("14:00", "21:30").plot(
        #     title=sym + "' candles", figsize=(26, 12))

        sub_df['date'] = [mdates.date2num(d) for d in sub_df.index]
        sub_df.reset_index()
        quotes = [tuple(x) for x in sub_df[['date', 'open', 'high', 'low', 'close']].values]
        self._fig, self._ax = plt.subplots(figsize=(20, 10))
        candlestick_ohlc(self._ax, quotes, colorup='g', width=0.0003, alpha=1)

        self._ax.xaxis_date()
        self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))

        day_profit = 0.0
        success = 0
        total = 0.0
        for position in self.trading_session.get_positions_between_dates(
                symbol,
                market_open,
                market_close):
            self.draw_position(position)
            profit = position.get_profit()
            day_profit += profit
            total += 1
            if profit > 0:
                success += 1

        plt.axvline(pd.Timestamp(market_open), color='black', linestyle=':')
        plt.axvline(pd.Timestamp(market_close), color='black', linestyle=':')
        sub_df["SMMA 20"].plot()
        sub_df["SMMA 50"].plot()
        ratio = 0 if total == 0 else success/total
        plt.title("{}'s candles on {}\nProfit: {:.2f}$, Ratio: {:.2f}%".format(
            symbol,
            date,
            day_profit,
            ratio
        ))

        if save_pic:
            plt.savefig(self.result_folder + "/" + str(date) + "-" + symbol + ".png")
            plt.close()
        else:
            plt.show()
            plt.close()

    def draw_all(self, symbols):
        # sub_df = self.market_data[self.market_data.index.day == 9].between_time("14:00", "21:30")
        # We are only getting one day but we should be really iterating over all days
        for sym in symbols:
            md = self.market_data[sym]
            sub_df = md.loc[md.index.day == 9].between_time("11:00", "23:30")
            # sub_df['close'].between_time("14:00", "21:30").plot(
            #     title=sym + "' candles", figsize=(26, 12))

            sub_df['date'] = [mdates.date2num(d) for d in sub_df.index]
            sub_df.reset_index()
            quotes = [tuple(x) for x in sub_df[['date', 'open', 'high', 'low', 'close']].values]
            self._fig, self._ax = plt.subplots(figsize=(20, 10))
            candlestick_ohlc(self._ax, quotes, colorup='g', width=0.0003, alpha=1)
            # sub_df['slow_ma'].between_time("14:00", "21:30").plot()
            # sub_df['fast_ma'].between_time("14:00", "21:30").plot()
            # sub_df['med_ma'].between_time("14:00", "21:30").plot()
            self._ax.xaxis_date()
            self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))

            day_profit = 0.0
            for position in self.trading_session.get_positions(sym):
                self._ax.add_patch(
                    self._position_to_rectangle(position)
                )
                day_profit += position.get_profit()
            plt.axvline(pd.Timestamp(market_open), color='black', linestyle=':')
            plt.axvline(pd.Timestamp(market_close), color='black', linestyle=':')
            plt.title(sym + "{}'s candles")
            plt.show()

    def draw_position(self, position: Position):
        open_time = mdates.date2num(position.get_open_datetime())
        close_time = mdates.date2num(position.get_close_datetime())
        open_price = position.get_open_price()
        close_price = position.get_close_price()
        color = "green" if position.get_profit() > 0 else "red"
        rec = Rectangle(
            (open_time,
             open_price),
            close_time - open_time,
            close_price - open_price,
            facecolor=color,
            alpha=0.2
        )
        self._ax.add_patch(rec)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        message = "Position: {}\nEntry $ : {:.2f}$\nProfit  : {:.2f}$".format(
            position.side,
            open_price,
            position.get_profit()
        )
        self._ax.text(open_time,
                      max(open_price, close_price) + 0.5,
                      message,
                      fontsize=10,
                      verticalalignment='top',
                      bbox=props)

    def save_to_file(self, file):
        self._fig.savefig(file)
        plt.close(self._fig)

    def add_indicator(self, indicator, in_chart: bool = True):
        self._indicators.append({
            "name": indicator.name,
            "indicator": indicator,
            "in chart": in_chart
        })

    @ property
    def title(self):
        return self._title

    @ title.setter
    def title(self, val):
        self._title = val

    @ property
    def market_data(self):
        return self._market_data

    @ market_data.setter
    def market_data(self, val):
        self._market_data = val

    @ property
    def symbol(self):
        return self._symbol

    @ symbol.setter
    def symbol(self, val):
        self._symbol = val

    @ property
    def trading_session(self):
        return self._trading_session

    @ trading_session.setter
    def trading_session(self, val):
        self._trading_session = val

    @ property
    def result_folder(self):
        return self._result_folder

    @ result_folder.setter
    def result_folder(self, val):
        self._result_folder = val

# import os
# import sys
# import numpy as np
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

class EquityChart():
    pass

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

    def draw_date(self, symbol, date):

        md = self.market_data[symbol]
        start_date = datetime(date.year, date.month, date.day, 0, 0)
        market_open = datetime(date.year, date.month, date.day, 14, 30)
        end_date = datetime(date.year, date.month, date.day, 23, 59)
        market_close = datetime(date.year, date.month, date.day, 21, 0)
        # print(type(date))
        # print(type(md.index))
        # print(md.loc[md.index == date])
        md["SMA 20"] = md["close"].rolling(window=20).mean()
        datetime_mask = (md.index >= start_date) & (md.index <= end_date)
        sub_df = md.loc[datetime_mask].between_time("14:00", "21:30")
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

        for position in self.trading_session.get_positions_between_dates(
                symbol,
                market_open,
                market_close):
            self._ax.add_patch(
                self._position_to_rectangle(position)
            )
        plt.axvline(pd.Timestamp(market_open), color='black', linestyle=':')
        plt.axvline(pd.Timestamp(market_close), color='black', linestyle=':')
        sub_df["SMA 20"].plot()
        plt.title(symbol + "' candles")
        plt.show()

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

            for position in self.trading_session.get_positions(sym):
                self._ax.add_patch(
                    self._position_to_rectangle(position)
                )
            plt.axvline(pd.Timestamp('2020-10-09 14:30'), color='black', linestyle=':')
            plt.axvline(pd.Timestamp('2020-10-09 21:00'), color='black', linestyle=':')
            plt.title(sym + "' candles")
            plt.show()

    def _position_to_rectangle(self, position: Position):
        open_time = mdates.date2num(position.get_open_datetime())
        close_time = mdates.date2num(position.get_close_datetime())
        open_price = position.get_open_price()
        close_price = position.get_close_price()
        color = "green" if position.get_profit() > 0 else "red"
        return Rectangle(
            (open_time,
             open_price),
            close_time - open_time,
            close_price - open_price,
            facecolor=color,
            alpha=0.2
        )

    def save_to_file(self, file):
        self._fig.savefig(file)
        plt.close(self._fig)

    def add_indicator(self, indicator, in_chart: bool = True):
        self._indicators.append({
            "name": indicator.name,
            "indicator": indicator,
            "in chart": in_chart
        })

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, val):
        self._title = val

    @property
    def market_data(self):
        return self._market_data

    @market_data.setter
    def market_data(self, val):
        self._market_data = val

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, val):
        self._symbol = val

    @property
    def trading_session(self):
        return self._trading_session

    @trading_session.setter
    def trading_session(self, val):
        self._trading_session = val

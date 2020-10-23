# import os
# import sys
# import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import matplotlib.ticker as plticker
# import matplotlib.patches as patches
# from matplotlib.patches import Rectangle
# from matplotlib.dates import DateFormatter
from mplfinance.original_flavor import candlestick_ohlc


class EquityChart():
    pass

class TradeChart():
    def __init__(self):
        self._title = None
        self._indicators = []
        self._market_data = None

    def add_position(self, position):
        self.positions.append(position)

    def draw(self, day):
        sub_df = self.market_data[self.market_data.index.day == 9].between_time("14:00", "21:30")
        sub_df['Close'].between_time("14:00", "21:30").plot(
            title=self.title + " close price", figsize=(26, 12))

        sub_df['date'] = [mdates.date2num(d) for d in sub_df.index]
        sub_df.reset_index()
        quotes = [tuple(x) for x in sub_df[['date', 'Open', 'High', 'Low', 'Close']].values]
        fig, ax = plt.subplots(figsize=(20, 10))
        candlestick_ohlc(ax, quotes, colorup='g', width=0.0003, alpha=1)
        sub_df['slow_ma'].between_time("14:00", "21:30").plot()
        sub_df['fast_ma'].between_time("14:00", "21:30").plot()
        sub_df['med_ma'].between_time("14:00", "21:30").plot()
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))

    def save_to_file(self, file):
        pass

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

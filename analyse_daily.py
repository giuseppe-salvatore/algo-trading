import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from indicators.bollinger_bands import BollingerBands


def analyse_daily_charts(date):

    path = "data/minute_charts/" + date
    file_array = []

    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                file_array.append(os.path.join(r, file))

    for file in file_array:
        print("Analysing " + file)

        plt.style.use('default')

        headers = ['date', 'open', 'close', 'high', 'low','volume']
        dtypes = {'date': 'str', 'open': 'float', 'high': 'float', 'low': 'float',
                  'close': 'float', 'volume': 'int'}
        # df = pd.read_csv(file, index_col='date', parse_dates=[
                        #  'date'], dtype=dtypes, sep=',', header=1, names=headers)
        df = pd.read_csv(file, index_col=0, parse_dates=True, dtype=dtypes, sep=',', header=1, names=headers)
        print(df)
        df['date'] = df.index
        df['date'] = [mdates.date2num(d) for d in df['date']]
        quotes = [tuple(x)
                  for x in df[['date', 'open', 'high', 'low', 'close']].values]
        print(df)
        max = float('-inf')
        min = float('+inf')
        open = df['open'][0]
        close = df['close'][len(df)-1]

        for elem in df['high']:
            if elem > max:
                max = elem
        for elem in df['low']:
            if elem < min:
                min = elem

        max_perc_var = (max - min) / min * 100.0
        oc_perc_var = (close - open) / open * 100.0
        print("  max = " + str(max))
        print("  min = " + str(min))
        print("  ope = " + str(open))
        print("  clo = " + str(close))
        print("  max perc = " + "{:.2f}".format(max_perc_var) + "%")
        print("  oc perc = " + "{:.2f}".format(oc_perc_var) + "%")

        stock = file.split("/")[-1].replace(".csv", "")

        fig, ax = plt.subplots()
        
        #df['close'].plot(title=stock, label="Close Price", ax=ax)
        mean = df['close'].rolling(5).mean()

        # interpolated = df['close'].interpolate(method='linear')
        #mean.plot(label='5 SMA', ax=ax)
        # interpolated.plot(label='Poly Interpolation', ax=ax)
        # diff = mean.diff() * 10 + df['open'][0]
        # ax.axhline(y=df['open'][0], xmin=-1,
        #                    xmax=1, color='black', linestyle='--', lw=2)
        # diff.rolling(2).mean().plot(label="Diff", ax=ax)
        bollinger_bands = BollingerBands({
            "median_period": 5,
            "stdev_factor": 2,
            "source": "close"
        })
        bollinger_bands.calculate(df)
        bollinger_bands.bands_dataframe['upper band'].plot(
            label='Upper band', ax=ax, color='green')
        bollinger_bands.bands_dataframe['lower band'].plot(
            label='Lower band', ax=ax, color='green')
        bollinger_bands.bands_dataframe['mean'].plot(
            label='Mean band', ax=ax, color='orange')
        #candlestick_ohlc(ax, quotes, width=0.5/(24*60), colorup='green', colordown='red', alpha=0.8)
        candlestick_ohlc(ax, quotes, width=0.7/(24*60), colorup='green', colordown='red', alpha=0.8)
        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        #ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        # ax.set_facecolor('black')
        # ax.figure.set_facecolor('#121212')
        # ax.tick_params(axis='x', colors='white')
        # ax.tick_params(axis='y', colors='white')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.grid()
        plt.legend()
        plt.show()


if __name__ == "__main__":

    dates = ["2020-07-29"]

    for date in dates:
        print("Analysing charts of " + date)
        analyse_daily_charts(date)

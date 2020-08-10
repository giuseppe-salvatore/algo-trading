import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
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
        max = float('-inf')
        min = float('+inf')
        df = pd.read_csv(file, index_col='time',parse_dates=['time'])
        
        for elem in df['high']:
            if elem > max:
                max = elem
        for elem in df['low']:
            if elem < min:
                min = elem
        print("  max = " + str(max))
        print("  min = " + str(min))
        print("  ope = " + str(df['open'][0]))
        print("  clo = " + str(df['close'][len(df)-1]))

        stock = file.split("/")[-1].replace(".csv","")

        fig, ax = plt.subplots()
        df['close'].plot(title=stock, label="Close Price", ax=ax)
        mean = df['close'].rolling(5).mean()
        interpolated = df['close'].interpolate(method='linear')
        mean.plot(label='5 SMA', ax=ax)
        interpolated.plot(label='Poly Interpolation', ax=ax)
        diff = mean.diff() * 10 + df['open'][0]
        ax.axhline(y=df['open'][0], xmin=-1,
                           xmax=1, color='black', linestyle='--', lw=2)
        diff.rolling(2).mean().plot(label="Diff", ax=ax)
        bollinger_bands = BollingerBands({
            "median_period": 5,
            "stdev_factor": 2,
            "source": "close"
        })
        bbdf = bollinger_bands.calculate(df)
        bbdf['upper band'].plot(label='Upper band', ax=ax)
        bbdf['lower band'].plot(label='Lower band', ax=ax)
        bbdf['mean'].plot(label='Lower band', ax=ax)
        plt.grid()
        plt.legend()
        plt.show()



if __name__ == "__main__":

    dates = ["2020-07-29"]

    for date in dates:
        print("Analysing charts of " + date)
        analyse_daily_charts(date)
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt



def analyse_daily_charts(date):
    path = "../data/minute_charts/" + date
    file_array = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                file_array.append(os.path.join(r, file))
    for file in file_array:
        print("Analysing " + file)
        max = float('-inf')
        min = float('+inf')
        df = pd.read_csv(file)
        
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

        stock = file.split("/")[-1]
        df['close'].plot(title=stock, label="Close Price")
        mean = df['close'].rolling(7).mean()
        mean.plot(label='5 SMA')
        diff = mean.diff() * 10 + 51 
        diff.rolling(2).mean().plot(label="Diff")
        plt.grid()
        plt.legend()
        plt.show()



if __name__ == "__main__":

    dates = ["2020-07-02"]

    for date in dates:
        print("Analysing charts of " + date)
        analyse_daily_charts(date)
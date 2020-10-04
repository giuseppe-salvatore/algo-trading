import sys
import time
import datetime
import numpy as np
import pandas as pd
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from lib.trading.alpaca import AlpacaTrading




NY = 'America/New_York'

def main(symbol):
    api = AlpacaTrading()

    #symbol = 'AAPL'
    barset = api.get_minute_barset(symbol)

    open = float(barset[symbol][0].o)

    times = []
    values = [] 
    opens = []
    closes = []
    highs = []
    lows = []
    volumes = []

    for elem in barset:
        print("Barset for " + elem + " has " + str(len(barset[elem]))  + " elements")
        for bar in barset[elem]:
            
            curr_time = bar.t
            if curr_time.day == 26 and ((curr_time.hour == 9 and curr_time.minute >= 30) or curr_time.hour >= 10):
                print(bar)
                times.append(str(curr_time))
                
                print(bar.t, end="")
                opens.append(float(bar.o))
                closes.append(float(bar.c))
                highs.append(float(bar.h))
                lows.append(float(bar.l))
                volumes.append(float(bar.v))

                print(" perc: " + "{:.3f}".format((closes[-1] - opens[-1]) / open * 100) + "%")
                #print(pd.Timestamp(bar.t, unit='s', tz_convert=NY))

    dataframe = pd.DataFrame(None,pd.DatetimeIndex(times),None)
    
    #dataframe["Time"] = np.array(times)
    #dataframe = dataframe.astype({'Time':'datetime64[ns]'})
    dataframe["Open"] = np.array(opens)
    dataframe["Close"] = np.array(closes)
    dataframe["High"] = np.array(highs)
    dataframe["Low"] = np.array(lows)
    dataframe['Volume'] = np.array(volumes)
    dataframe['5 min mean'] = dataframe['Close'].rolling(window=5).mean()
    dataframe['UpperBB'] = dataframe['5 min mean'] + 2*dataframe['Close'].rolling(window=5).std()
    dataframe['LowerBB'] = dataframe['5 min mean'] - 2*dataframe['Close'].rolling(window=5).std()
    #dataframe['BB Divergence'] = dataframe['UpperBB'] - dataframe['LowerBB']
    plot_with_matplotlib(dataframe, symbol)

def plot_with_finplot(dataframe):
    ax,ax2 = fplt.create_plot(symbol, rows=2)
    candles = dataframe[['Open','Close','High','Low']]
    fplt.plot(dataframe['5 min mean'], ax=ax, legend='ma-5')
    fplt.plot(dataframe['UpperBB'], ax=ax, legend='UpperBB')
    fplt.plot(dataframe['LowerBB'], ax=ax, legend='LowerBB')
    #fplt.plot(dataframe['BB Divergence'], ax=ax, legend='Divergence')
    fplt.candlestick_ochl(candles, ax=ax)

    volumes = dataframe[['Open','Close','Volume']]
    fplt.volume_ocv(volumes, ax=ax2)
    #dataframe["CHK"].plot(label='MFA',figsize=(12,8),title='Prices')    
    #fplt.legend()
    fplt.show()

def plot_with_matplotlib(dataframe, stock):
    #dataframe[['Close']].plot(title=stock)
    plt.clf()
    dataframe['Moving AVG 3'] = dataframe['Close'].rolling(window=3).mean()
    dataframe['Derivate'] = dataframe['Close'].diff() / 3.0 
    dataframe['Moving AVG 3'].plot(title=stock,label='Moving AVG 3')
    dataframe['Moving AVG 10'] =  dataframe['Close'].rolling(window=10).mean()
    dataframe['Moving AVG 10'].plot(label='Moving AVG 10')
    dataframe['Exp Moving AVG 10'] = dataframe['Close'].ewm(com=5).mean()
    dataframe['Exp Moving AVG 10'].plot()
    plt.grid()
    #dataframe[['Derivate']].plot()
    plt.legend(loc='center center')
    plt.grid()
    plt.show()
    #plt.draw()
    #plt.pause(0.01)


#def play(dataframe):



if __name__ == "__main__":

    while True:
        main(sys.argv[1])
        time.sleep(30)
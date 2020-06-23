import time
import datetime
import numpy as np
import pandas as pd
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from api_proxy import TradeApiProxy




NY = 'America/New_York'

def main():
    api = TradeApiProxy()

    symbol = 'AAPL'
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
        print("Barset for " + elem)
        for bar in barset[elem]:
            
            curr_time = bar.t
            if curr_time.day == 19:
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
    ax,ax2 = fplt.create_plot(symbol, rows=2)
    candles = dataframe[['Open','Close','High','Low']]
    fplt.plot(dataframe['5 min mean'], ax=ax, legend='ma-25')
    fplt.plot(dataframe['UpperBB'], ax=ax, legend='UpperBB')
    fplt.plot(dataframe['LowerBB'], ax=ax, legend='LowerBB')
    fplt.candlestick_ochl(candles, ax=ax)

    volumes = dataframe[['Open','Close','Volume']]
    fplt.volume_ocv(volumes, ax=ax2)
    #dataframe["CHK"].plot(label='MFA',figsize=(12,8),title='Prices')    
    #fplt.legend()
    fplt.show()
    

if __name__ == "__main__":
    main()
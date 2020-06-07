import time
import requests
import datetime
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi


def get_from_secrets(key):
    f = open(".secrets","r")
    value = None
    for line in f:
        if key in line:
            value = line.split("=")[1].strip()
    f.close()
    return value

ALPACA_API_KEY = get_from_secrets("ALPACA_API_KEY")
ALPACA_SECRET = get_from_secrets("ALPACA_SECRET")
TIINGO_API_KEY = get_from_secrets("TIINGO_API_KEY")

TIINGO_API_URL = "https://api.tiingo.com/iex"

#API endpoint URL
ALPACA_PAPER_TRADING_API_URL = "https://paper-api.alpaca.markets"
ALPACA_DATA_API_URL = "https://data.alpaca.markets" 

#api_version v2 refers to the version that we'll use
#very important for the documentation
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET, ALPACA_PAPER_TRADING_API_URL, api_version='v2')
data_api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET, ALPACA_DATA_API_URL, api_version='v1')

r=requests.get("http://www.example.com/", headers={"content-type":"text"})

#Init our account var
account = api.get_account()

print(account.status)

# Lists currently open trades
positions = api.list_positions()
print(positions)

earnings = api.polygon.earnings(['BA'])
print(earnings)

# Daily OHLCV dataframe
#aapl_daily = api.polygon.historic_agg('day', 'AAPL', limit=1000).df
#print(aapl_daily)


headers = {"APCA-API-KEY-ID": ALPACA_API_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET}

stocks_list = ['BA','TSLA','AAL','AMD','INTC','NVDA']
stocks_price = {'BA': [],'TSLA': [],'AAL': [],'AMD': [],'INTC': [],'NVDA': []}

dt_index = None
data = []
timing = []


def fetch_data(stock_name):
    response = requests.get(ALPACA_DATA_API_URL + "/v1/last/stocks/" + stock_name, headers=headers)
    status = response.json().get('status')
    if status == 'success':
        latest_timestamp = response.json().get('last').get('timestamp')
        last_price = float(response.json().get('last').get('price'))        
        stocks_price[stock_name].append(last_price)

f = open("dump.dat","a")
f.write("time")
for stock in stocks_list:
    print("|{:7s}".format(stock),end="",flush=True)
    f.write("," + stock)

print("")
f.write("\b\n")

plots = {}
idx = 1
for stock in stocks_list:
    plots[stock] = plt.figure(idx)
    idx += 1
    break

plt.ion()
plt.show()


try:
    while True:

        now = datetime.datetime.now()
        timing.append(now)
        dt_index = pd.DatetimeIndex(timing)
        dataframe = pd.DataFrame(None, dt_index, None)
        f.write(str(now)[:16])
        for stock in stocks_list:
            fetch_data(stock)
            time.sleep(0.5)
            print("|{:7.2f}".format(stocks_price[stock][-1]),end="",flush=True)
            f.write(",{:.2f}".format(stocks_price[stock][-1]))

        print("")
        f.write("\n")
        for key in stocks_price.keys():
            #data[:,:-1] = np.array(stocks_price[key])
            #np.append(data,np.array(stocks_price[key]),axis=0)
            dataframe[key] = np.array(stocks_price[key])
        plt.clf()
        #dataframe['BA'].plot(label='Boeing',figsize=(12,8),title='Prices')
        #dataframe['TSLA'].plot(label='Tesla',figsize=(12,8),title='Prices')
        #dataframe['AAL'].plot(label='American Airline')
        dataframe['AMD'].plot(label='AMD',figsize=(12,8),title='Prices')
        #dataframe['INTC'].plot(label='Intel')
        #dataframe['NVDA'].plot(label='NVidia')
        plt.legend()
        plt.draw()
        plt.pause(0.005)
        time.sleep(55)

except:
    f.flush()
finally:
    f.close()



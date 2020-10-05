'''
Documentation on the streaming api can be found here
https://alpaca.markets/docs/api-documentation/api-v2/streaming/
'''
import time
import json
import pytz
import requests
import datetime
import websocket
import traceback
import numpy as np
import pandas as pd
import conf.secret as config
import matplotlib.pyplot as plt
import script.investment as invst

values = {}
localFormat = "%Y-%m-%d %H:%M:%S"
timezone = 'America/New_York'

stocks_list = invst.get_portfolio_stocks()

header_printed = False

class Bar():

    def __init__(self, object):
        self.object = object

def print_header():

    global header_printed
    if header_printed:
        return
    header_printed = True

    print("\n\n\n\n\n\n\n\n\n")
    print("|{:20s}".format("latests"), end="")
    for stock in stocks_list:
        print("|    {:5s}     ".format(stock), end="")
    print("|{:7s}".format("TOTAL"), end="")
    print("|", flush=True)

def print_gains(time_updated):
    try:
        print("", end="\r", flush=True)
        print("|{:20s}".format(str(time_updated)[:19]), end="")
        for stock in stocks_list:
            if stock in values:
                print("|({:5.1f}) {:6.1f}".format(
                    values[stock][-1][1],
                    invst.get_capital_gain_for(stock, values[stock][-1][1])), end="")
            else:
                print("|({:5s}) {:6s}".format("----", "----"), end="")
        print("|{:7.2f}".format(invst.get_total_capital_gain()), end="")
        print("|", end="", flush=True)
    except:
        traceback.print_exc()


def handle_quote(message):
    ticker = message["data"].get("T")
    price = message["data"].get("P")
    # tstamp = message["data"].get("t")

    if ticker not in values:
        values[ticker] = []

    if len(values[ticker]) > 0:
        # Get the latest price and record the new one only if differs
        # from the latest to save memory
        # if values[ticker][-1][1] > price + 0.05 or values[ticker][-1][1] < price - 0.1:
        # if values[ticker][-1][1] != price:
        utcnow_naive = datetime.datetime.utcnow()
        utcnow = utcnow_naive.replace(tzinfo=pytz.utc)
        newYorkTime = utcnow.astimezone(pytz.timezone(timezone))

        if newYorkTime.minute == values[ticker][-1][0].minute:
            values[ticker][-1] = [newYorkTime, price]
            print_gains(newYorkTime)
        else:
            values[ticker].append([newYorkTime, price])
            print_gains(newYorkTime)
    else:
        utcnow_naive = datetime.datetime.utcnow()
        utcnow = utcnow_naive.replace(tzinfo=pytz.utc)
        newYorkTime = utcnow.astimezone(pytz.timezone(timezone))
        values[ticker].append([newYorkTime, price])


def handle_trade(message):
    print(message)


def handle_bar(message):
    print(message)


handlers = {"T": handle_trade, "Q": handle_quote, "AM": handle_bar}


def on_open(ws):

    message = {
        "action": "authenticate",
        "data": {
            "key_id": config.ALPACA_API_KEY,
            "secret_key": config.ALPACA_SECRET
        }
    }

    # Failure might happen if you are already connected with the same account...
    # you will get something like this
    # {"stream":"listening","data":{"error":"your connection is rejected while
    # another connection is open under the same account"}}
    print("Sending auth message \n" + json.dumps(message))
    ws.send(json.dumps(message))

    streams = []

    for stock in stocks_list:
        # streams.append("Q." + stock)
        streams.append("AM." + stock)

    message = {
        "action": "listen",
        "data": {
            "streams": streams
        }
    }
    print("Sending subscription message \n" + json.dumps(message))
    ws.send(json.dumps(message))


def on_message(ws, message):

    my_dict = None

    try:
        my_dict = json.loads(message)

        if "stream" in my_dict:
            if "data" in my_dict:
                if "ev" in my_dict["data"]:
                    # This will call the appropriate handler given the type of message
                    print_header()
                    handlers[my_dict["data"]["ev"]](my_dict)
                else:
                    print(message)
            else:
                print(message)
        else:
            print("Unexpected message:   " + message)
    except:
        traceback.print_exc()


def on_close(ws):
    print("Closing")

    try:
        bytes = 0
        for stock in values:
            f = open("quotes_" + stock, "a")
            bytes += len(values[stock]) * (len(values[stock][0][0]) + 4)
            for price in values[stock]:
                print(stock + " " + str(price[1]) + "  " + str(price[0])[:19])
                f.write(str(price[0])[:19] + "," + str(price[1]) + "\n")
            f.close()

        for stock in values:
            f = open("quotes_" + stock, "r")
            timing = []
            prices = []
            for line in f:
                tokens = line.split(",")
                timing.append(tokens[0].strip())
                prices.append(float(tokens[1].strip()))
            dt_index = pd.DatetimeIndex(timing)
            dataframe = pd.DataFrame(None, dt_index, None)
            dataframe[stock] = np.array(prices)
            dataframe[stock].plot(label=stock, figsize=(12, 8), title='Prices')
            plt.legend()
            plt.show()
        print("Total bytes: " + bytes)
    except:
        traceback.print_exc()


def on_error(ws, error):
    print(error)

def rest_init():
    headers = {"APCA-API-KEY-ID": config.ALPACA_API_KEY,
               "APCA-API-SECRET-KEY": config.ALPACA_SECRET}

    stocks_price = {'BA': [], 'TSLA': [], 'AAL': [],
                    'AMD': [], 'INTC': [], 'NVDA': []}

    dt_index = None
    timing = []

    def fetch_data(stock_name):
        response = requests.get(
            config.ALPACA_DATA_REST_ENDPOINT + "/v1/last/stocks/" + stock_name, headers=headers)
        status = response.json().get('status')
        if status == 'success':
            latest_timestamp = response.json().get('last').get('timestamp')
            last_price = float(response.json().get('last').get('price'))
            stocks_price[stock_name].append(last_price)

    f = open("dump.dat", "a")
    f.write("time")
    for stock in stocks_list:
        print("|{:7s}".format(stock), end="", flush=True)
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
                print("|{:7.2f}".format(
                    stocks_price[stock][-1]), end="", flush=True)
                f.write(",{:.2f}".format(stocks_price[stock][-1]))

            print("")
            f.write("\n")
            for key in stocks_price.keys():
                # data[:,:-1] = np.array(stocks_price[key])
                # np.append(data,np.array(stocks_price[key]),axis=0)
                dataframe[key] = np.array(stocks_price[key])
            plt.clf()
            # dataframe['BA'].plot(label='Boeing',figsize=(12,8),title='Prices')
            # dataframe['TSLA'].plot(label='Tesla',figsize=(12,8),title='Prices')
            # dataframe['AAL'].plot(label='American Airline')
            dataframe['AMD'].plot(label='AMD', figsize=(12, 8), title='Prices')
            # dataframe['INTC'].plot(label='Intel')
            # dataframe['NVDA'].plot(label='NVidia')
            plt.legend()
            plt.draw()
            plt.pause(0.005)
            time.sleep(55)

    except:
        f.flush()
    finally:
        f.close()


def main():

    while True:
        try:
            ws = websocket.WebSocketApp(
                config.ALPACA_WEBSOCKET_ENDPOINT,
                on_open=on_open,
                on_message=on_message,
                on_close=on_close,
                on_error=on_error)
            ws.run_forever()
            print("Received error")
            time.sleep(2)
            print("Trying to re-establish connection")
            time.sleep(10)
        except KeyboardInterrupt as e:
            print(e)
            break
    print("End of main")


if __name__ == "__main__":
    main()

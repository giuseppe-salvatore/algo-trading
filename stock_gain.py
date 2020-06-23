import time
import config
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi



def open_connection():
    '''
    By default this will open a connection to the pater trading endpoint
    so no real money will be used for your transactions. To use a founded
    account and real money use config.ALPACA_REAL_TRADING_REST_ENDPOINT
    insead of config.ALPACA_PAPER_TRADING_REST_ENDPOINT
    '''

    # Make sure you set your API key and secret in the config module     
    api = tradeapi.REST(
        config.ALPACA_API_KEY,
        config.ALPACA_SECRET,
        config.ALPACA_PAPER_TRADING_REST_ENDPOINT,
        api_version='v2'
    )

    return api


def check_account(api):
    
    # Get our account information.
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    balance_change = float(account.equity) - float(account.last_equity)
    # Check how much money we can use to open new positions.
    print("\r",end="",flush=True)
    print('Equity is ${} balance change: ${:.2f}'.format(account.equity,balance_change), end="", flush=True)

    return account.equity
    

def create_baseline():

    initial_values = {}

    return initial_values

def list_orders(api):

    orders = api.list_orders(status='all')

    for order in orders:
        if order.status == 'filled':
            print(order.symbol + " " + order.filled_avg_price)

def list_positions(api):
    positions = api.list_positions()

    for pos in positions:
        print("|{:>6s} ".format(pos.symbol), end="")
    print("")

    for pos in positions:
        print("|{:>6s} ".format(pos.current_price), end="")
    print("")

    for pos in positions:
        print(pos.symbol + " gain is " + "{:.2f}".format(float(pos.market_value) - float(pos.cost_basis)))

def list_assets(api):

    assets = api.list_assets()
    for asset in assets:
        print(asset)
    print("There are " + str(len(assets)) + " available")

def get_cost_basis(api):

    positions = api.list_positions()

    cost_basis = {}
    for pos in positions:
        cost_basis[pos.symbol] = float(pos.cost_basis)

    return cost_basis

def append_to_market_value(api, gain):

    positions = api.list_positions()

    for pos in positions:
        if pos.symbol in gain:
            gain[pos.symbol].append(float(pos.market_value) - float(pos.cost_basis))
        else: 
            gain[pos.symbol] = [float(pos.market_value) - float(pos.cost_basis)]

def main_loop(api):
    equity = check_account(api)
    now = datetime.datetime.now()

    time_array = []
    stock_array = []

    time_array.append(now)
    stock_array.append(float(equity))
    

    date_index = pd.DatetimeIndex(time_array)
    dataframe = pd.DataFrame(None, date_index, None)
    dataframe["Equity"] = np.array(stock_array)

    while True:

        time.sleep(30)
        plt.clf()

        equity = check_account(api)
        now = datetime.datetime.now()

        stock_array.append(float(equity))
        time_array.append(now)
        
        date_index = pd.DatetimeIndex(np.array(time_array))
        dataframe = pd.DataFrame(None, date_index, None)
        dataframe["Equity"] = np.array(stock_array)
        dataframe["Equity"].plot(label="equity", figsize=(12, 8), title='Equity value')
        plt.legend()
        plt.draw()
        plt.pause(0.005)

def main():

    api = open_connection()
    list_positions(api)

    
    time_array = []
    gain = {}
    append_to_market_value(api, gain)
    time_array.append(datetime.datetime.now())
    #date_index = pd.DatetimeIndex(np.array(time_array))
    #dataframe = pd.DataFrame(None, date_index, None)
    idx = {}
    fig_printed = False
    legend = True
    while True:
        time.sleep(10)
        plt.clf()
        time_array.append(datetime.datetime.now())
        append_to_market_value(api, gain)
        date_index = pd.DatetimeIndex(np.array(time_array))
        dataframe = pd.DataFrame(None, date_index, None)
        
        for stock in gain:
            dataframe[stock] = np.array(gain[stock])
            #if not fig_printed:
            dataframe[stock].plot(label=stock, figsize=(12, 8), title='Gain per stock')
            #fig_printed = True
            #else:
            #    if stock not in idx:
            #        dataframe[stock].plot(label=stock)
            #        idx[stock] = 1
                #else:
                #    dataframe[stock].plot()
        
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.draw()
        plt.pause(0.005)


    
    


if __name__ == '__main__':
    main()
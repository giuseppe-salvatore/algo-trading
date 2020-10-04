import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi

from lib.trading.alpaca import AlpacaTrading



def get_equity(api):
    
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
    
def append_to_equity_file(date, equity_value):
    
    f = open("data/equity_history.dat","a")

    f.write(str(date) + "," + str(equity_value) + "\n")
    f.flush()
    f.close()


def load_equity_data():
        
    f = open("data/equity_history.dat","r")
    date = []
    equity_value = []

    for line in f:
        date.append(line.split(',')[0].strip())
        equity_value.append(float(line.split(',')[1].strip()))

    return date, equity_value    

status = "not_touching"
has_touched = False
statuses = []


profit = 0.0

portfolio = {

    "stock_name": 
        [
            {
                "shares" : 0.0, 
                "value" : 0.0 
            },
            {
                "shares" : 0.0, 
                "value" : 0.0 
            }        
        ]
    
}

stop_loss = {}

def buy(stock, current_value, number):
    if stock in portfolio:
        print("Bought " + str(number) + " of stocks at " + str(current_value))
        portfolio[stock].append({ "shares": number, "value": current_value })
    else:
        print("Bought " + str(number) + " of stocks at " + str(current_value))
        portfolio[stock] = [{ "shares": number, "value": current_value }]

    print_positions(stock)

def has_stock_at_least_shares(stock, shares):
    if get_shares(stock) >= shares:
        return True
    return False

def get_shares(stock):
    total_shares = 0.0
    if stock in portfolio:
         for position in portfolio[stock]:
             total_shares += position["shares"]

    return total_shares

def sell(stock, current_value, number):
    if stock not in portfolio:
        return False
    if has_stock_at_least_shares(stock, number):
        for shares in portfolio[stock]:
            if float(shares["shares"]) > number:
                print("Selling " + str(number) + " shares at " + str(shares["value"]))
                shares["shares"] = float(shares["shares"]) - number
            elif float(shares["shares"]) < number:
                number = number - float(shares["shares"])
                print("Selling " + str(number) + " shares at " + str(shares["value"]))
                del shares
            else:
                print("Selling " + str(number) + " shares at " + str(shares["value"]))
                del shares

        
    return 0
    
def set_stop_loss(stock, loss_threshold):
    global stop_loss
    print("Setting stop loss for " + stock + " at " + str(loss_threshold))
    stop_loss[stock] = loss_threshold

def is_below_stop_loss_threshold(stock, current_value):
    if stop_loss[stock] > current_value:
        return True
    return False

def sell_all_remaining_stocks(stock):
    if stock in portfolio:
        for shares in portfolio[stock]:
            print("Selling " + str(shares["shares"]) + " at " + str(shares["value"]) + " for a total cost of " + str(float(shares["shares"]) + float(shares["value"])))
        del portfolio[stock]
        del stop_loss[stock]

def own_shares_of(stock):
    if stock in portfolio:
        len(portfolio[stock])
    return 

MAX_LOSS_IN_PERCENTAGE = 0.5

def has_stop_loss_set(stock):
    if stock in stop_loss:
        return True 
    return False

def get_loss_threshold_value(value):
    return get_two_decimal(value * (100.0 - MAX_LOSS_IN_PERCENTAGE) / 100.00)

def loss_has_been_detected(stock, curr_value):
    if stock in stop_loss:
        if curr_value < stop_loss[stock]:
            print("Loss detected at " + str(curr_value) + " stop loss at " + str(stop_loss[stock]))
            return True
    return False

def get_position_value(stock):
    value = 0.0
    if stock in portfolio:
        for position in portfolio[stock]:
            value += position["shares"] * position["value"]
    return get_two_decimal(value)

def get_market_value(stock, current_value):
    value = 0.0
    if stock in portfolio:
        for position in portfolio[stock]:
            value += position["shares"] * current_value
    return get_two_decimal(value)

def print_positions(stock):
    if stock in portfolio:
        for position in portfolio[stock]:
            shares = position["shares"]
            value = position["value"]
            print("   " + str(shares) + " shares at " + str(value) + " total = " + str(get_two_decimal(shares * value)))
        print("   Total value: " + str(get_position_value(stock)))

def get_instant_gain_percentage(stock, current_value):
    
    position_value = get_position_value(stock)

    if position_value == 0:
        return 0.0
    #print(" Perc calc " + str(get_market_value(stock, current_value)) + " - " + str(position_value) + " = " + str(get_market_value(stock, current_value) - position_value))    
    return (get_market_value(stock, current_value) - position_value) / position_value * 100.0


def get_two_decimal(value):
    return float("{:.2f}".format(value))

def play_strategy(time_array, stock_array):

    global has_touched
    global statuses
    global status

    incremental_time = []
    incremental_values = []
    for i in range(0, len(time_array)):
        incremental_time.append(time_array[i])
        curr_stock_value = get_two_decimal(stock_array[i])
        prev_stock_value = curr_stock_value
        if i > 0:
            prev_stock_value = stock_array[i-1]
        incremental_values.append(curr_stock_value)

        date_index = pd.DatetimeIndex(incremental_time)
        dataframe = pd.DataFrame(None, date_index, None)
        time.sleep(0.1)   
        plt.clf()
        dataframe["Stock Values"] = np.array(incremental_values)
        dataframe["Stock Values"].plot(label="Stock Values", figsize=(12, 8), title='A Stock')
        dataframe["Stock Values Mean"] = dataframe.rolling(window=3).mean()["Stock Values"]
        dataframe["Stock Values Mean"].plot(label="Mean")
        dataframe.rolling(window=10).min()["Stock Values Mean"].plot(label="Mean Min")  
        dataframe["Actual Min"] = dataframe.rolling(window=10).min()["Stock Values"]
        dataframe["Actual Min"].plot(label="Actual Min")

        if dataframe["Stock Values"][i] == dataframe["Actual Min"][i]:
            print(str(i) + " " + "{:.2f}".format(curr_stock_value) + " " + str(get_instant_gain_percentage("AAPL",curr_stock_value)) +  "% Touching", end="")
            status = "touching"
            has_touched = True
            
        else:
            print(str(i) + " " + "{:.2f}".format(curr_stock_value) + " " + str(get_instant_gain_percentage("AAPL",curr_stock_value)) + "% Not Touching", end="")
            status = "not_touching"
        statuses.append(status) 

        if loss_has_been_detected("AAPL", curr_stock_value):
            sell_all_remaining_stocks("AAPL")

        if has_touched and statuses[i] == "not_touching" and statuses[i-1] == "touching":
            print("Departed")
            buy("AAPL", curr_stock_value, 100)
            set_stop_loss("AAPL", get_loss_threshold_value(curr_stock_value))
        else:
            print("")

        if has_touched and has_stop_loss_set("AAPL") and curr_stock_value > prev_stock_value:
            set_stop_loss("AAPL", get_loss_threshold_value(curr_stock_value))

        plt.legend()
        plt.draw()
        plt.pause(0.005)


def main():

    api = open_connection()

    time_array = []
    stock_array = []

    time_array, stock_array = load_equity_data()
    play_strategy(time_array,stock_array)

    # equity = get_equity(api)
    # now = datetime.datetime.now()

    # time_array.append(now)
    # stock_array.append(float(equity))    

    date_index = pd.DatetimeIndex(time_array)
    dataframe = pd.DataFrame(None, date_index, None)
    dataframe["Equity"] = np.array(stock_array)

    while True:

        #append_to_equity_file(now, equity)

        time.sleep(5)
        plt.clf()

        # equity = get_equity(api)
        # now = datetime.datetime.now()

        # stock_array.append(float(equity))
        # time_array.append(now)
        
        date_index = pd.DatetimeIndex(np.array(time_array))
        dataframe = pd.DataFrame(None, date_index, None)
        dataframe["Equity"] = np.array(stock_array)
        dataframe["Equity"].plot(label="equity", figsize=(12, 8), title='Equity value')
        dataframe.rolling(window=10).mean()["Equity"].plot(label="Mean")
        plt.legend()
        plt.draw()
        plt.pause(0.005)
        


if __name__ == '__main__':
    main()
import os
import sys
import time
import math
import json
import datetime
import numpy as np
import pandas as pd
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from api_proxy import TradeApiProxy
from stockstats import StockDataFrame

import strategies.scalping.recommended_stocks
#import recommended_stocks


# def get_symbols():
#     symbols = ""
#     for symbol in strategies.scalping.recommended_stocks.stocks:
        
#         #print("Searching for " + symbol, end="")

#         symbols += symbol + ","
        
#         #if len(barset[symbol]) > 0:
#         #    print(" SUCCESS")
#         #else:
#         #    print(" FAILED")

    # return symbols

class DummyScalping():
    def __init__(self):
        self.params = dict()
        self.params["reward_perc"] = 2.0
        self.params["stop_loss_perc"] = 1
        self.params["enter_per_variation_signal"] = 0.5
        self.reward_perc = 2.0
        self.stop_loss_perc = 1
        self.enter_per_variation_signal = 0.5

        self.options["sell_before_market_closes"] = True
        self.options["ignore_first_trades"] = True
        self.options["exit_when_reward_target_is_hit"] = False

algo = DummyScalping()

def get_symbols():

    return "ZM "

def build_dataframe(barset, symbol):

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

            if bar.c > 800:
                return None
            
            if bar.c < 5:
                return None

            if curr_time.day == 26 and ((curr_time.hour == 9 and curr_time.minute >= 30) or curr_time.hour >= 10):
            
                times.append(str(bar.t))
                opens.append(float(bar.o))
                closes.append(float(bar.c))
                highs.append(float(bar.h))
                lows.append(float(bar.l))
                volumes.append(float(bar.v))

    df = pd.DataFrame(None,pd.DatetimeIndex(times),None)
    
    #dataframe["Time"] = np.array(times)
    #dataframe = dataframe.astype({'Time':'datetime64[ns]'})
    df["open"] = np.array(opens)
    df["close"] = np.array(closes)
    df["high"] = np.array(highs)
    df["low"] = np.array(lows)
    df['volume'] = np.array(volumes)

    date = '26th'
    month = 'June'

    if not os.path.exists('data/minute_charts/' + date + '_' + month + '/'):
        os.makedirs('data/minute_charts/' + date + '_' + month + '/')
        df.to_csv('data/minute_charts/' + date + '_' + month + '/' + symbol + '.csv')

    return df


TARGET_START_THRESHOLD = 0.5

current_positions = {}

START_EQUITY = 25000.0
equity = START_EQUITY

def short(stock, value, quant):
    global equity
    global current_positions
    print("Making a short position " + str(quant) + " " + str(value) + "$")

    if stock not in current_positions:
        current_positions[stock] = { "quantity" : -quant, "value" : value }
        equity -= (value * -quant)

profits = {}

def liquidate(stock, curr_val):
    global equity
    global profits
    global current_positions

    if stock in current_positions:
        current_position = current_positions[stock]
        print("Start equity is " + str(equity))
        profit = (curr_val - current_position["value"]) * float(current_position["quantity"])
        print("Profit for this trade is: " + str(profit))
        equity += curr_val * float(current_position["quantity"])
        print("Updated equity is " + str(equity))
        print("")

        if stock not in profits:
            profits[stock] = [profit]            
        else:
            profits[stock].append(profit)

        del current_positions[stock]

def long(stock, value, quant):
    global equity
    global current_positions
    print("Making a long position " + str(quant) + " " + str(value) + "$")

    if stock not in current_positions:
        current_positions[stock] = { "quantity" : quant, "value" : value }
        equity -= (value * quant)

def value_close_to_thousand(value):
    rem = round(1000.0  / value)
    
    if rem * value > 1100:
        return rem - 1
    return rem

LIQUIDATE_THRESHOLD = 0.5
MAX_THRESHOLD_RESET = 2


def play(stock, perc_df, dataframe):

    global current_positions
    i = 0    
    in_position = False
    start = perc_df[0]
    liquidate_threshold = 0
    reset_threshold = 0
    position = ""
    market_closing_soon = False
    dataframe['long'] = dataframe['close']
    dataframe['short'] = dataframe['close']
    dataframe['liq'] = dataframe['close']
    local_min = float('inf')
    local_max = float('-inf')
    threshold_reset = 0
    for el in perc_df:
        if i < 3:
            dataframe['long'][i] = np.nan
            dataframe['short'][i] = np.nan
            dataframe['liq'][i] = np.nan
            i += 1
            continue
        #print("Curr=" + str(el) + " Start=" + str(start) + " Diff=" + str(el-start))
        if len(dataframe['close']) - i <= 10:
            market_closing_soon = True
        if not in_position and not market_closing_soon:
            if (el - start) > algo.enter_per_variation_signal:
                quant = value_close_to_thousand(dataframe['close'][i])
                long(stock, dataframe['close'][i], quant)
                dataframe['long'][i] = dataframe['Perc Var'][i]
                dataframe['short'][i] = np.nan
                dataframe['liq'][i] = np.nan
                liquidate_threshold = el - algo.stop_loss_perc
                reset_threshold = el + algo.reward_perc
                position = "long"
                in_position = True
            elif (el - start) < -algo.enter_per_variation_signal:
                quant = value_close_to_thousand(dataframe['close'][i])
                short(stock, dataframe['close'][i], quant)
                dataframe['short'][i] = dataframe['Perc Var'][i]
                dataframe['long'][i] = np.nan
                dataframe['liq'][i] = np.nan
                liquidate_threshold = el + algo.stop_loss_perc
                reset_threshold = el - algo.reward_perc
                position = "short"
                in_position = True
            else:
                dataframe['long'][i] = np.nan
                dataframe['short'][i] = np.nan
                dataframe['liq'][i] = np.nan        
        else:
            if not market_closing_soon:
                if position == "long":
                    if el >= reset_threshold:
                        reset_threshold = el + algo.reward_perc
                        liquidate_threshold = el - algo.stop_loss_perc
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = np.nan
                        threshold_reset += 1
                    elif el <= liquidate_threshold:
                        liquidate(stock, dataframe['close'][i])
                        start = el
                        in_position = False
                        position = ""
                        threshold_reset = 0                        
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = dataframe['Perc Var'][i]
                    else:
                        if local_max > dataframe['close'][i]:
                            local_max = dataframe['close'][i]
                            reset_threshold = local_max + algo.reward_perc
                            liquidate_threshold = local_max - algo.stop_loss_perc                
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = np.nan

                        local_min = float('inf')
                        local_max = float('-inf')
                else:
                    if el <= reset_threshold:
                        reset_threshold = el - algo.reward_perc
                        liquidate_threshold = el + (algo.stop_loss_perc)
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = np.nan
                        threshold_reset += 1
                    elif el >= liquidate_threshold:
                        liquidate(stock, dataframe['close'][i])
                        start = el
                        in_position = False
                        position = ""
                        threshold_reset = 0
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = dataframe['Perc Var'][i]

                        
                        local_min = float('inf')
                        local_max = float('-inf')
                    else:
                        if local_min < dataframe['close'][i]:
                            local_min = dataframe['close'][i]
                            reset_threshold = local_min - algo.reward_perc
                            liquidate_threshold = local_min + (algo.stop_loss_perc) 
                        dataframe['long'][i] = np.nan
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = np.nan
            else:
                if in_position:
                    liquidate(stock, dataframe['close'][i])
                    start = el
                    in_position = False
                    position = ""
                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan
                    dataframe['liq'][i] = dataframe['Perc Var'][i]
                else:
                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan
                    dataframe['liq'][i] = np.nan


        i += 1
    


def run_strategy(api):
    global equity
    global profits
    global current_positions

    symbols = get_symbols()

    # symbols = ['F',
    # 'BAC',
    # 'GE',
    # 'CSCO',
    # 'T',
    # 'FB',
    # 'AMD',
    # 'TWTR',
    # 'MSFT',
    # 'AAPL',
    # 'BA',
    # 'UBER',
    # 'SIRI',
    # 'PINS',
    # 'DAL',
    # 'WORK',
    # 'INTC',
    # 'CCL',
    # 'C',
    # 'JPM',
    # 'HPQ',
    # 'ABEV',
    # 'MS',
    # 'BABA',
    # 'ORCL',
    # 'GM',
    # 'DIS',
    # 'MPC',
    # 'V',
    # 'TSLA',
    # 'PYPL',
    # 'NFLX'
    # ]

    symbols = ['HPQ']

    used_stocks = []

    #barset = api.get_5_minutes_barset(symbols)

    gains = {}

    for s in symbols:
        equity = START_EQUITY
        barset = api.get_minute_barset(s)


        df = build_dataframe(barset, s)
        if df is None:
            print("Skipping " + s)
            continue
        
        used_stocks.append(s)    

        stock_df = StockDataFrame.retype(df)
        #stock_df['close'].plot(title=symbols)
        #stock_df['SMA 5'] = stock_df['close'].rolling(window=5).mean()
        stock_df['Perc Var'] = (stock_df['close'] - stock_df['close'][0])/stock_df['close'][0] * 100
        #stock_df['MIN'] = stock_df['close'].rolling(window=5).min()
        #stock_df['MAX'] = stock_df['close'].rolling(window=5).max()
        #stock_df['SMA 5 of 5'] = stock_df['SMA 5'].rolling(window=5).mean()
        stock_df['Perc Var'].plot(label='Perc Var')
        #stock_df['SMA 5 of 5'].plot(label='SMA 5 of 5')
        #stock_df['rsi_3'].plot(title=symbols)
        #stock_df['MIN'].plot(label='MIN')
        #stock_df['MAX'].plot(label='MAX')

        play(s, stock_df['Perc Var'],stock_df)
        stock_df['long'].plot(marker="^", color="green")
        stock_df['short'].plot(marker="v",color="red")
        stock_df['liq'].plot(marker="o",color="orange")

        print("Total gain for " + s + " = " + str(equity - START_EQUITY))
        gains[s] = (equity - START_EQUITY)

    print("")
    print("")
    print("")
    print("")
    total_gain = 0.0
    for s in gains:
        print("Total gain for " + s + " = " + str(gains[s]))
        total_gain += gains[s]
    print('Overall Total Gain: ' + str(total_gain))

    f = open("strategies/scalping/backtesting/schema.json", "r")
    schema = json.load(f)

    amount_gained = 0.0
    amount_lost = 0.0
    per_stock_profit = {}
    for stock in profits:
        per_stock_gain = 0.0
        good_trades = 0
        bad_trades = 0
        for pr in profits[stock]:
            per_stock_gain += pr
            if pr > 0:
                good_trades += 1
                amount_gained += pr
            else:
                bad_trades += 1
                amount_lost += (-pr)
        schema["total trades"] += good_trades + bad_trades
        schema["good trades"] += good_trades
        schema["bad trades"] += bad_trades
        per_stock_profit[stock] = per_stock_gain

        print(stock + " profit: " + str(per_stock_gain))
        print("  good: " + str(good_trades))
        print("  bad : " + str(bad_trades))
    print('Overall Total Gain: ' + str(total_gain))

    profit_df = pd.DataFrame({ 'stocks': list(per_stock_profit.keys()), 'gain': list(per_stock_profit.values())})
    profit_df.plot.bar(x='stocks', y='gain', rot=0)

    schema["symbols"] =  used_stocks
    schema["initial capital"] = float("{:.2f}".format(START_EQUITY))
    schema["final capital"] = float("{:.2f}".format(START_EQUITY + total_gain))
    schema["percentage gain"] = "{:.2f}%".format((schema["final capital"] - schema["initial capital"]) / schema["initial capital"] * 100.0)
    schema["total gain"] = float("{:.2f}".format(total_gain))
    schema["amount gained"] = float("{:.2f}".format(amount_gained))
    schema["amount lost"] = float("{:.2f}".format(amount_lost))
    
    json.dumps(schema,indent=4)


    with open("strategies/scalping/backtesting/results.json","w") as output:
        json.dump(schema,output,indent=4)

    print(current_positions)
    plt.legend()
    plt.xticks(rotation=90)
    plt.grid()
    plt.show()




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
import strategies.scalping.recommended_stocks


from api_proxy import TradeApiProxy
from stockstats import StockDataFrame


class DummyScalping():

    def __init__(self):
        self.params = dict()
        self.params["day"] = 30
        self.params["month"] = 6
        self.params["reward_perc"] = 3.0
        self.params["stop_loss_perc"] = 0.5
        self.params["enter_per_variation_signal"] = 0.5
        self.params["bars_to_ignore_at_market_open"] = 4
        
        self.options = dict()
        self.options["sell_before_market_closes"] = True        
        self.options["ignore_first_trades"] = True
        self.options["exit_when_reward_target_is_hit"] = False
        self.options["exclude_cheap_stocks"] = True
        self.options["exclude_expensive_stocks"] = True

        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.profits = dict()
        self.current_positions = dict()

    def play(self, stock, perc_df, dataframe):

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
                if (el - start) > self.params["enter_per_variation_signal"]:
                    quant = self.value_close_to_thousand(dataframe['close'][i])
                    self.long(stock, dataframe['close'][i], quant)
                    dataframe['long'][i] = dataframe['Perc Var'][i]
                    dataframe['short'][i] = np.nan
                    dataframe['liq'][i] = np.nan
                    liquidate_threshold = el - self.params["stop_loss_perc"]
                    reset_threshold = el + self.params["reward_perc"] 
                    position = "long"
                    in_position = True
                elif (el - start) < -self.params["enter_per_variation_signal"]:
                    quant = self.value_close_to_thousand(dataframe['close'][i])
                    self.short(stock, dataframe['close'][i], quant)
                    dataframe['short'][i] = dataframe['Perc Var'][i]
                    dataframe['long'][i] = np.nan
                    dataframe['liq'][i] = np.nan
                    liquidate_threshold = el + self.params["stop_loss_perc"]
                    reset_threshold = el - self.params["reward_perc"] 
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
                            reset_threshold = el + self.params["reward_perc"] 
                            liquidate_threshold = el - self.params["stop_loss_perc"] 
                            dataframe['long'][i] = np.nan
                            dataframe['short'][i] = np.nan
                            dataframe['liq'][i] = np.nan
                            threshold_reset += 1
                        elif el <= liquidate_threshold:
                            self.liquidate(stock, dataframe['close'][i])
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
                                reset_threshold = local_max + self.params["reward_perc"] 
                                liquidate_threshold = local_max - self.params["stop_loss_perc"] 
                            dataframe['long'][i] = np.nan
                            dataframe['short'][i] = np.nan
                            dataframe['liq'][i] = np.nan

                            local_min = float('inf')
                            local_max = float('-inf')
                    else:
                        if el <= reset_threshold:
                            reset_threshold = el - self.params["reward_perc"] 
                            liquidate_threshold = el + (self.params["stop_loss_perc"] )
                            dataframe['long'][i] = np.nan
                            dataframe['short'][i] = np.nan
                            dataframe['liq'][i] = np.nan
                            threshold_reset += 1
                        elif el >= liquidate_threshold:
                            self.liquidate(stock, dataframe['close'][i])
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
                                reset_threshold = local_min - self.params["reward_perc"] 
                                liquidate_threshold = local_min + self.params["stop_loss_perc"] 
                            dataframe['long'][i] = np.nan
                            dataframe['short'][i] = np.nan
                            dataframe['liq'][i] = np.nan
                else:
                    if in_position:
                        self.liquidate(stock, dataframe['close'][i])
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

    def tick_within_market_hours(self, tick, day, month):
        if (tick.day == day and 
            tick.month == month and
            ((tick.hour == 9 and tick.minute >= 30) or 
            (tick.hour >= 10 and tick.hour < 16 ) or tick.hour == 16 and tick.minute == 0)):
            return True
        return False

    def build_dataframe(self, barset, symbol):

        times = []
        values = []
        opens = []
        closes = []
        highs = []
        lows = []
        volumes = []

        for elem in barset:
            #print("Barset for " + elem + " has " +
            #      str(len(barset[elem])) + " elements")
            for bar in barset[elem]:

                curr_time = bar.t

                if self.options["exclude_expensive_stocks"]:
                    if bar.c > 1200:
                        return None

                if self.options["exclude_cheap_stocks"]:
                    if bar.c < 5:
                        return None

                if self.tick_within_market_hours(curr_time, self.params["day"], self.params["month"]):

                    times.append(str(bar.t))
                    opens.append(float(bar.o))
                    closes.append(float(bar.c))
                    highs.append(float(bar.h))
                    lows.append(float(bar.l))
                    volumes.append(float(bar.v))

        df = pd.DataFrame(None, pd.DatetimeIndex(times), None)

        #dataframe["Time"] = np.array(times)
        #dataframe = dataframe.astype({'Time':'datetime64[ns]'})
        df["open"] = np.array(opens)
        df["close"] = np.array(closes)
        df["high"] = np.array(highs)
        df["low"] = np.array(lows)
        df['volume'] = np.array(volumes)

        date = str(self.params["day"]) + 'th'
        month = 'June'
        base_dir = 'data/minute_charts/'

        if not os.path.exists(base_dir + date + '_' + month + '/'):
            os.makedirs(base_dir + date + '_' + month + '/')

        df.to_csv(base_dir + date + '_' + month + '/' + symbol + '.csv')

        return df

    def get_symbols(self):
        return strategies.scalping.recommended_stocks.stocks
        #return ['V']

    def run_strategy(self, api):

        symbols = self.get_symbols()

        used_stocks = []

        #barset = api.get_5_minutes_barset(symbols)

        gains = {}

        for s in symbols:
            self.current_capital = self.start_capital
            barset = api.get_minute_barset(s)

            df = self.build_dataframe(barset, s)
            if df is None:
                #print("Skipping " + s)
                continue

            used_stocks.append(s)

            stock_df = StockDataFrame.retype(df)
            # stock_df['close'].plot(title=symbols)
            #stock_df['SMA 5'] = stock_df['close'].rolling(window=5).mean()
            stock_df['Perc Var'] = (
                stock_df['close'] - stock_df['close'][0])/stock_df['close'][0] * 100
            #stock_df['MIN'] = stock_df['close'].rolling(window=5).min()
            #stock_df['MAX'] = stock_df['close'].rolling(window=5).max()
            #stock_df['SMA 5 of 5'] = stock_df['SMA 5'].rolling(window=5).mean()
            stock_df['Perc Var'].plot(label='Perc Var')
            #stock_df['SMA 5 of 5'].plot(label='SMA 5 of 5')
            # stock_df['rsi_3'].plot(title=symbols)
            # stock_df['MIN'].plot(label='MIN')
            # stock_df['MAX'].plot(label='MAX')

            self.play(s, stock_df['Perc Var'], stock_df)
            #stock_df['long'].plot(marker="^", color="green")
            #stock_df['short'].plot(marker="v", color="red")
            #stock_df['liq'].plot(marker="o", color="orange")

            #print("Total gain for " + s + " = " +
            #      str(self.current_capital - self.start_capital))
            gains[s] = (self.current_capital - self.start_capital)

        #print("")
        #print("")
        total_gain = 0.0
        for s in gains:
            #print("Total gain for " + s + " = " + str(gains[s]))
            total_gain += gains[s]
        #print('Overall Total Gain: ' + str(total_gain))

        f = open("strategies/scalping/backtesting/schema.json", "r")
        schema = json.load(f)

        amount_gained = 0.0
        amount_lost = 0.0
        per_stock_profit = {}
        for stock in self.profits:
            per_stock_gain = 0.0
            good_trades = 0
            bad_trades = 0
            for pr in self.profits[stock]:
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

            #print(stock + " profit: " + str(per_stock_gain))
            #print("  good: " + str(good_trades))
            #print("  bad : " + str(bad_trades))
        #print('Overall Total Gain: ' + str(total_gain))

        profit_df = pd.DataFrame({
            'stocks': list(per_stock_profit.keys()),
            'gain': list(per_stock_profit.values())
        })
        #profit_df.plot.bar(x='stocks', y='gain', rot=0)

        schema["symbols"] = used_stocks
        schema["initial capital"] = float("{:.2f}".format(self.start_capital))
        schema["final capital"] = float(
            "{:.2f}".format(self.start_capital + total_gain))
        schema["percentage gain"] = "{:.2f}%".format(
            (schema["final capital"] - schema["initial capital"]) / schema["initial capital"] * 100.0)
        schema["total gain"] = float("{:.2f}".format(total_gain))
        schema["amount gained"] = float("{:.2f}".format(amount_gained))
        schema["amount lost"] = float("{:.2f}".format(amount_lost))

        json.dumps(schema, indent=4)
        now = str(datetime.datetime.now())
        with open("strategies/scalping/backtesting/results-" + now + ".json", "w") as output:
            json.dump(schema, output, indent=4)

        return schema["total gain"]

        #print(self.current_positions)
        # plt.legend()
        # plt.xticks(rotation=90)
        # plt.grid()
        # plt.show()

    def short(self, stock, value, quant):

        #print("Making a short position " + str(quant) + " " + str(value) + "$")

        if stock not in self.current_positions:
            self.current_positions[stock] = {
                "quantity": -quant, "value": value}
            self.current_capital -= (value * -quant)

    def liquidate(self, stock, curr_val):
        if stock in self.current_positions:
            current_position = self.current_positions[stock]
            #print("Start equity is " + str(self.current_capital))
            profit = (
                curr_val - current_position["value"]) * float(current_position["quantity"])
            #print("Profit for this trade is: " + str(profit))
            self.current_capital += curr_val * \
                float(current_position["quantity"])
            #print("Updated equity is " + str(self.current_capital))
            #print("")

            if stock not in self.profits:
                self.profits[stock] = [profit]
            else:
                self.profits[stock].append(profit)

            del self.current_positions[stock]

    def long(self, stock, value, quant):
        #print("Making a long position " + str(quant) + " " + str(value) + "$")
        if stock not in self.current_positions:
            self.current_positions[stock] = {"quantity": quant, "value": value}
            self.current_capital -= (value * quant)

    def value_close_to_thousand(self, value):
        rem = round(1000.0 / value)

        if rem * value > 1100:
            return rem - 1
        return rem

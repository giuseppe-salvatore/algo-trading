import os
import sys
import time
import math
import json
import logging
import traceback
import datetime
import operator
import itertools
import numpy as np
import pandas as pd
import multiprocessing as mp
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import strategies.scalping.recommended_stocks


from api_proxy import TradeApiProxy
from stockstats import StockDataFrame
from strategies.model import StockMarketStrategy


class MovingAverageConvDivReversal(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = dict()
        #self.params["reward_perc"] = 3.0
        #self.params["stop_loss_perc"] = 0.5
        #self.params["enter_per_variation_signal"] = 0.5
        #self.params["bars_to_ignore_at_market_open"] = 4
        self.params["ma_fast_period"] = 3
        self.params["ma_slow_period"] = 15
        self.params["sell_before_market_closes"] = 5

        self.ma_slow = self.params["ma_slow_period"]
        self.ma_fast = self.params["ma_fast_period"]
        self.ma_slow_str = "MA " + str(self.ma_slow)
        self.ma_fast_str = "MA " + str(self.ma_fast)

        self.options = dict()
        self.options["ignore_first_trades"] = True
        self.options["exit_when_reward_target_is_hit"] = False
        self.options["exclude_cheap_stocks"] = True
        self.options["exclude_expensive_stocks"] = True
        self.options["early_buy"] = True

        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.profits = dict()
        self.current_positions = dict()

        self.name = "macd_reversal"
        self.results_folder = "strategies/" + self.name + "/backtesting/"

    def set_fast_ma(self, val):
        self.params["ma_fast_period"] = val
        self.ma_fast = self.params["ma_fast_period"]
        self.ma_fast_str = "MA " + str(self.ma_fast)

    def set_slow_ma(self, val):
        self.params["ma_slow_period"] = val
        self.ma_slow = self.params["ma_slow_period"]
        self.ma_slow_str = "MA " + str(self.ma_slow)

    def simulate(self, stock, dataframe):

        logging.info("Runing simulation on " + stock)
        i = 0
        in_position = False
        start = dataframe['Perc Var'][0]
        liquidate_threshold = 0
        reset_threshold = 0
        position = ""
        market_closing_soon = False
        dataframe['long'] = np.full([len(dataframe['Perc Var'])], np.nan)
        dataframe['short'] = np.full([len(dataframe['Perc Var'])], np.nan)
        dataframe['liq'] = np.full([len(dataframe['Perc Var'])], np.nan)
        dataframe[self.ma_slow_str] = dataframe['Perc Var'].rolling(
            window=self.ma_slow).mean()
        dataframe[self.ma_fast_str] = dataframe['Perc Var'].rolling(
            window=self.ma_fast).mean()
        local_min = float('inf')
        local_max = float('-inf')
        threshold_reset = 0
        buy_signal = False
        sell_signal = False

        previous_above = None
        current_above = None

        for el in dataframe['Perc Var']:

            if len(dataframe['close']) - i <= self.params["sell_before_market_closes"]:
                market_closing_soon = True

            # No data available
            if np.isnan(dataframe[self.ma_slow_str][i]):
                if self.options['early_buy'] and not in_position and not np.isnan(dataframe[self.ma_fast_str][i]):
                    if dataframe[self.ma_fast_str][i] < 0:
                        print("Generating sell signal")
                        sell_signal = True
                    else:
                        print("Generating buy signal")
                        buy_signal = True

                    dataframe['liq'][i] = np.nan
                else:
                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan
                    dataframe['liq'][i] = np.nan
                    i += 1
                    continue
            else:
                dataframe['long'][i] = np.nan
                dataframe['short'][i] = np.nan
                dataframe['liq'][i] = np.nan
                previous_above = current_above
                if dataframe[self.ma_slow_str][i] > dataframe[self.ma_fast_str][i]:
                    current_above = self.ma_slow_str
                else:
                    current_above = self.ma_fast_str

                if current_above != None and previous_above != None:
                    if current_above != previous_above:
                        if current_above == self.ma_fast_str:
                            buy_signal = True
                            #print("Generated buy signal")
                        else:
                            sell_signal = True
                            #print("Generated sell signal")

            if not in_position and not market_closing_soon:
                if buy_signal is True:
                    quant = self.value_close_to_threshold(dataframe['close'][i])
                    self.long(stock, dataframe['close'][i], quant, dataframe['time'][i])
                    buy_signal = False
                    dataframe['long'][i] = dataframe['Perc Var'][i]
                    position = "long"
                    in_position = True
                else:
                    dataframe['long'][i] = np.nan

                if sell_signal is True:
                    quant = self.value_close_to_threshold(dataframe['close'][i])
                    self.short(stock, dataframe['close'][i], quant, dataframe['time'][i])
                    sell_signal = False
                    position = "short"
                    in_position = True
                    dataframe['short'][i] = dataframe['Perc Var'][i]
                else:
                    dataframe['short'][i] = np.nan

                dataframe['liq'][i] = np.nan

            elif in_position and not market_closing_soon:
                if buy_signal or sell_signal:
                    self.liquidate(stock, dataframe['close'][i], dataframe['time'][i])
                    dataframe['liq'][i-1] = dataframe['Perc Var'][i]
                    if buy_signal:
                        self.long(stock, dataframe['close'][i], quant, dataframe['time'][i])
                        dataframe['long'][i] = dataframe['Perc Var'][i]
                        dataframe['short'][i] = np.nan
                        dataframe['liq'][i] = np.nan
                        position = "long"
                    elif sell_signal:
                        self.short(stock, dataframe['close'][i], quant,dataframe['time'][i])
                        dataframe['short'][i] = dataframe['Perc Var'][i]
                        dataframe['long'][i] = np.nan
                        dataframe['liq'][i] = np.nan
                        position = "short"

                    buy_signal = False
                    sell_signal = False
                else:
                    dataframe['liq'][i] = np.nan
                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan

            elif in_position and market_closing_soon:
                buy_signal = False
                sell_signal = False
                self.liquidate(stock, dataframe['close'][i], dataframe['time'][i])
                dataframe['liq'][i] = dataframe['Perc Var'][i]
                position = ""
                in_position = False

                dataframe['long'][i] = np.nan
                dataframe['short'][i] = np.nan

            i += 1

    def run_strategy(self, api):

        try:
            symbols = self.get_symbols()
            used_stocks = []

            gains = {}

            base_data_dir = self.get_bars_data_folder()

            for s in symbols:
                self.current_capital = self.start_capital

                df = None
                symbol_data_file_name = base_data_dir + s + ".csv"
                if os.path.exists(symbol_data_file_name):
                    df = pd.read_csv(symbol_data_file_name)                    
                else:
                    raise Exception("Dataset file not available")

                if df is None:
                    continue

                used_stocks.append(s)

                sdf = df
                # stock_df['close'].plot(title=symbols)
                #stock_df['SMA 5'] = stock_df['close'].rolling(window=5).mean()
                sdf['Perc Var'] = (
                    sdf['close'] - sdf['close'][0])/sdf['close'][0] * 100
                #stock_df['MIN'] = stock_df['close'].rolling(window=5).min()
                #stock_df['MAX'] = stock_df['close'].rolling(window=5).max()
                #stock_df['SMA 5 of 5'] = stock_df['SMA 5'].rolling(window=5).mean()

                rsfld = self.results_folder + "/" + s + ".png"
                #os.makedirs(self.results_folder + "/" + s)
                # ==============> stock_df['Perc Var'].plot(label=s).get_figure().savefig(rsfld)

                #stock_df['SMA 5 of 5'].plot(label='SMA 5 of 5')
                # stock_df['rsi_3'].plot(title=symbols)
                # stock_df['MIN'].plot(label='MIN')
                # stock_df['MAX'].plot(label='MAX')

                self.simulate(s, sdf)
                gains[s] = (self.current_capital - self.start_capital)
                
                fig, ax = plt.subplots()
                sdf['Perc Var'].plot(grid=True,
                                    title=s + " profit: " + str(gains[s]),
                                    legend=True,
                                    label='Close Price',
                                    marker="x",
                                    ax=ax,
                                    figure=fig,
                                    figsize=(12, 8))
                sdf[self.ma_slow_str].plot(grid=True,
                                        legend=True,
                                        color="purple",
                                        alpha=0.7,
                                        label=self.ma_slow_str,
                                        ax=ax,
                                        figure=fig)
                sdf[self.ma_fast_str].plot(grid=True,
                                        legend=True,
                                        color="orange",
                                        alpha=0.7,
                                        label=self.ma_fast_str,
                                        ax=ax,
                                        figure=fig)
                sdf['long'].plot(grid=True,
                                legend=True,
                                marker="^",
                                color="green",
                                ax=ax,
                                figure=fig)
                sdf['short'].plot(grid=True,
                                legend=True,
                                marker="v",
                                color="red",
                                ax=ax,
                                figure=fig)
                sdf['liq'].plot(grid=True,
                                legend=True,
                                marker="o",
                                color="orange",
                                ax=ax,
                                figure=fig)
                fig.savefig(rsfld)
                plt.close(fig)

            # print("Total gain for " + s + " = " +
            #      str(self.current_capital - self.start_capital))
            #gains[s] = (self.current_capital - self.start_capital)

            total_gain = 0.0
            for s in gains:
                #print("Total gain for " + s + " = " + str(gains[s]))
                total_gain += gains[s]

            print("Strategy with " +
                self.ma_fast_str + " " + self.ma_slow_str + " daily return: " + str(total_gain))

            # f = open("strategies/scalping/backtesting/schema.json", "r")
            # schema = json.load(f)

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
                # schema["total trades"] += good_trades + bad_trades
                # schema["good trades"] += good_trades
                # schema["bad trades"] += bad_trades
                per_stock_profit[stock] = per_stock_gain

            #     #print(stock + " profit: " + str(per_stock_gain))
            #     #print("  good: " + str(good_trades))
            #     #print("  bad : " + str(bad_trades))
            # print('Overall Total Gain: ' + str(total_gain))

            per_stock_profit_sorted = dict(
                sorted(per_stock_profit.items(), key=operator.itemgetter(1), reverse=True))
            profit_df = pd.DataFrame({
                'stocks': list(per_stock_profit_sorted.keys()),
                'gain': list(per_stock_profit_sorted.values())
            })

            fig, ax = plt.subplots()
            profit_file_name = self.results_folder + "/profit_histogram.png"
            profit_df.plot.bar(title='Per stock profit', x='stocks',
                            y='gain', rot=90, ax=ax, figure=fig, grid=True)
            fig.savefig(profit_file_name)
            plt.close(fig)

        except Exception as e:
            print("Got exception " + str(e))
            traceback.print_tb(e.__traceback__)

        
        self.store_transactions()   

        return ["MCDA_" + self.ma_fast_str + "_" + self.ma_slow_str, total_gain]


    def generate_param_combination(self):
        ma_fast_period_param_values = range(4, 16)
        ma_slow_period_param_values = range(10, 31)
        #ma_fast_period_param_values = range(7, 8)
        #ma_slow_period_param_values = range(19, 20)
        param_product = itertools.product(
            ma_fast_period_param_values, ma_slow_period_param_values)
        result = []

        # We exclude the ones that have a constraint fail where the fast MA value is bigger than the slower MA
        for tup in param_product:
            if tup[0] < tup[1]:
                if (tup[1] - tup[0]) > 7:
                    result.append(tup)

        return result

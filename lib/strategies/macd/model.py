import os
import sys
import time
import math
import json
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

# logging.basicConfig(level='WARNING')
# log = logging.getLogger(__name__)
# log.setLevel('DEBUG')


class MovingAverageConvDiv(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = dict()
        self.params["ma_fast_period"] = None
        self.params["ma_slow_period"] = None
        self.params["sell_before_market_closes"] = 5

        self.ma_slow = self.params["ma_slow_period"]
        self.ma_fast = self.params["ma_fast_period"]
        self.ma_slow_str = "MA_" + str(self.ma_slow)
        self.ma_fast_str = "MA_" + str(self.ma_fast)

        self.options = dict()
        self.options["ignore_first_trades"] = True
        self.options["exit_when_reward_target_is_hit"] = False
        self.options["exclude_cheap_stocks"] = True
        self.options["exclude_expensive_stocks"] = True

        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.profits = dict()
        self.current_positions = dict()

        self.name = "macd"
        self.results_folder = "strategies/" + self.name + "/backtesting/"

        self.follow_max = False
        self.follow_min = False

    def set_fast_ma(self, val):
        self.params["ma_fast_period"] = val
        self.ma_fast = self.params["ma_fast_period"]
        self.ma_fast_str = "MA " + str(self.ma_fast)

    def set_slow_ma(self, val):
        self.params["ma_slow_period"] = val
        self.ma_slow = self.params["ma_slow_period"]
        self.ma_slow_str = "MA " + str(self.ma_slow)

    def init_helper_dataframes(self, dataframe):
        self.df = dataframe
        self.df['long'] = np.full([len(self.df['Perc Var'])], np.nan)
        self.df['short'] = np.full([len(self.df['Perc Var'])], np.nan)
        self.df['liq'] = np.full([len(self.df['Perc Var'])], np.nan)
        self.df[self.ma_fast_str] = self.df['Perc Var'].ewm(span=self.ma_fast, adjust = False).mean()
        self.df[self.ma_slow_str] = self.df['Perc Var'].ewm(span=self.ma_slow, adjust = False).mean()

    def simulate(self, stock, dataframe):

        log.debug("Runing simulation on " + stock)

        i = 0
        in_position = False
        start = dataframe['Perc Var'][0]        
        liquidate_threshold = 0
        reset_threshold = 0
        position = ""
        market_closing_soon = False

        self.init_helper_dataframes(dataframe)

        local_min = float('inf')
        local_max = float('-inf')
        threshold_reset = 0
        buy_signal = False
        sell_signal = False
        previous_above = None
        current_above = None

        assert(len(dataframe['Perc Var']) > 0)
        for el in dataframe['Perc Var']:

            try:

                if len(dataframe['close']) - i <= self.params["sell_before_market_closes"]:
                    log.debug("    Marked is closing soon")
                    market_closing_soon = True

                # No data available
                if dataframe[self.ma_slow_str][i] == np.nan:
                    print("Slow MA is still nan")
                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan
                    dataframe['liq'][i] = np.nan
                    print("Skipping because not a number")
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
                        quant = self.value_close_to_threshold(
                            dataframe['close'][i])
                        self.long(
                            stock, dataframe['close'][i], quant, dataframe['time'][i])
                        buy_signal = False
                        dataframe['long'][i] = dataframe['Perc Var'][i]
                        position = "long"
                        in_position = True
                    else:
                        dataframe['long'][i] = np.nan

                    if sell_signal is True:
                        quant = self.value_close_to_threshold(
                            dataframe['close'][i])
                        self.short(
                            stock, dataframe['close'][i], quant, dataframe['time'][i])
                        sell_signal = False
                        position = "short"
                        in_position = True
                        dataframe['short'][i] = dataframe['Perc Var'][i]
                    else:
                        dataframe['short'][i] = np.nan

                    dataframe['liq'][i] = np.nan

                elif in_position and not market_closing_soon:
                    if buy_signal or sell_signal:
                        buy_signal = False
                        sell_signal = False
                        self.liquidate(
                            stock, dataframe['close'][i], dataframe['time'][i])
                        dataframe['liq'][i] = dataframe['Perc Var'][i]
                        position = ""
                        in_position = False
                    else:
                        dataframe['liq'][i] = np.nan

                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan

                elif in_position and market_closing_soon:
                    buy_signal = False
                    sell_signal = False
                    self.liquidate(
                        stock, dataframe['close'][i], dataframe['time'][i])
                    dataframe['liq'][i] = dataframe['Perc Var'][i]
                    position = ""
                    in_position = False

                    dataframe['long'][i] = np.nan
                    dataframe['short'][i] = np.nan

                i += 1
            except Exception as e:
                print("Got exception at iteration " +
                      str(i) + " message " + str(e))
                traceback.print_tb(e.__traceback__)
                i += 1

    def run_strategy(self, api):

        try:
            symbols = self.get_symbols()
            used_stocks = []

            gains = {}

            base_data_dir = self.get_bars_data_folder()

            for s in symbols:

                log.debug("Running strategy on " + s)

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

                # stock_df['close'].plot(title=symbols)
                #stock_df['SMA 5'] = stock_df['close'].rolling(window=5).mean()
                df['Perc Var'] = (df['close'] - df['close']
                                  [0])/df['close'][0] * 100
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

                self.simulate(s, df)
                gains[s] = (self.current_capital - self.start_capital)

                fig, ax = plt.subplots()
                df['Perc Var'].plot(
                    title=s + " profit: " + str(gains[s]), legend=True, label='Close', ax=ax, figure=fig)
                df[self.ma_slow_str].plot(
                    legend=True, label=self.ma_slow_str, ax=ax, figure=fig)
                df[self.ma_fast_str].plot(
                    legend=True, label=self.ma_fast_str, ax=ax, figure=fig)
                df['long'].plot(legend=True, marker="^",
                                color="green", ax=ax, figure=fig)
                df['short'].plot(legend=True, marker="v",
                                 color="red", ax=ax, figure=fig)
                # sdf['liq'].plot(legend=True, marker="o",
                #                color="orange", ax=ax, figure=fig)
                fig.savefig(rsfld)
                plt.close(fig)

                # print("Total gain for " + s + " = " +
                #      str(self.current_capital - self.start_capital))
                #gains[s] = (self.current_capital - self.start_capital)

            total_gain = 0.0
            for s in gains:
                log.info("Total gain for " + s + " = " + str(gains[s]))
                total_gain += gains[s]

            log.debug("Strategy with " +
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
            logging.shutdown()
            print("Got exception " + str(e))
            traceback.print_tb(e.__traceback__)

        self.store_transactions()

        return ["MCDA_" + self.ma_fast_str + "_" + self.ma_slow_str, total_gain]

        # schema["symbols"] = used_stocks
        # schema["initial capital"] = float("{:.2f}".format(self.start_capital))
        # schema["final capital"] = float(
        #     "{:.2f}".format(self.start_capital + total_gain))
        # schema["percentage gain"] = "{:.2f}%".format(
        #     (schema["final capital"] - schema["initial capital"]) / schema["initial capital"] * 100.0)
        # schema["total gain"] = float("{:.2f}".format(total_gain))
        # schema["amount gained"] = float("{:.2f}".format(amount_gained))
        # schema["amount lost"] = float("{:.2f}".format(amount_lost))

        #json.dumps(schema, indent=4)
        #now = str(datetime.datetime.now())
        # with open("strategies/scalping/backtesting/results-" + now + ".json", "w") as output:
        #    json.dump(schema, output, indent=4)

        # return schema["total gain"]

    def generate_param_combination(self):
        ma_fast_period_param_values = range(5, 15)
        ma_slow_period_param_values = range(10, 30)
        param_product = itertools.product(
            ma_fast_period_param_values, ma_slow_period_param_values)
        result = []

        # We exclude the ones that have a constraint fail where the fast MA value is bigger than the slower MA
        for tup in param_product:
            if tup[0] < tup[1]:
                if (tup[1] - tup[0]) > 7:
                    result.append(tup)

        return result

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

# Indicators
from indicators.rsi import RSIIndicator

logging.basicConfig(level='WARNING')
log = logging.getLogger(__name__)
log.setLevel('INFO')


class RSIStrategyParams():
    def __init__(self):
        self.default_params = {
            # "Period": 7,
            "Upper Threshold": float(70),
            "Lower Threshold": float(30),
            "50 Cross Diff": float(10),
            # Could also be exit_threshold, max_in_threshold, strong_fifty_cross
            "Entry Signal": 'enter_threshold',
            "sell_before_market_closes": 5,
            "Upfront Samples": 3,
            "In-band Samples": 10
        }

        self.params = self.default_params

        #self.period = self.params["Period"]
        self.entry_signal = self.params["Entry Signal"]
        self.fifty_cross_diff = self.params["50 Cross Diff"]
        self.upper_threshold = self.params["Upper Threshold"]
        self.lower_threshold = self.params["Lower Threshold"]
        self.upfront_samples = self.params["Upfront Samples"]
        self.inband_samples = self.params["In-band Samples"]

        self.default_rsi_indicator = RSIIndicator(
            14,  # period
            6,  # mean_period
            'SMA',
            'close'
        )

        self.rsi_indicator = self.default_rsi_indicator

    # def set_period(self, period):
    #     self.period = period
    #     self.params["Period"] = period

    def set_limit_threshols(self, threshold):
        self.set_upper_threshold(100.0 - threshold)
        self.set_lower_threshold(threshold)

    def set_upper_threshold(self, upper_threshold):
        self.upper_threshold = upper_threshold
        self.params["Upper Threshold"] = upper_threshold

    def set_lower_threshold(self, lower_threshold):
        self.lower_threshold = lower_threshold
        self.params["Lower Threshold"] = lower_threshold

    def set_entry_signal(self, entry_signal):
        self.entry_signal = entry_signal
        self.params["Entry Signal"] = self.entry_signal

    def set_fifty_cross_diff(self, value):
        self.fifty_cross_diff = value
        self.params["50 Cross Diff"] = self.fifty_cross_diff

    def set_rsi_indicator(self, rsi_indicator: RSIIndicator):
        self.rsi_indicator = rsi_indicator


class RSIStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.long_name = "RSI Strategy"
        self.name = 'rsi'
        self.result_folder = "strategies/" + self.name + "/backtesting/"
        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.profits = dict()
        self.current_positions = dict()

    def calculate_rsi(self, dataframe):
        return self.params.rsi_indicator.calculate(dataframe)

    def init_helper_dataframes(self):
        df = self.get_df()
        df['long'] = np.full([len(df['Perc Var'])], np.nan)
        df['short'] = np.full([len(df['Perc Var'])], np.nan)
        df['liq'] = np.full([len(df['Perc Var'])], np.nan)
        df['rsi'] = self.calculate_rsi(df)
        df['rsi_buy'] = np.full([len(df['rsi'])], np.nan)
        df['rsi_sell'] = np.full([len(df['rsi'])], np.nan)

    def rsi_enter_lower_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        lower_threshold = self.params.lower_threshold
        if df['rsi'][index - 1] > lower_threshold and df['rsi'][index] < lower_threshold:
            return True
        return False

    def rsi_enter_upper_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        upper_threshold = self.params.upper_threshold
        if df['rsi'][index - 1] < upper_threshold and df['rsi'][index] > upper_threshold:
            return True
        return False

    def rsi_exit_lower_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        lower_threshold = self.params.lower_threshold
        if df['rsi'][index - 1] < lower_threshold and df['rsi'][index] > lower_threshold:
            return True
        return False

    def rsi_exit_upper_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        upper_threshold = self.params.upper_threshold
        if df['rsi'][index - 1] > upper_threshold and df['rsi'][index] < upper_threshold:
            return True
        return False

    def rsi_has_crossed_fifty_threshold_from_below(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        upper_threshold = self.params.upper_threshold
        if df['rsi'][index - 1] < upper_threshold and df['rsi'][index] > upper_threshold:
            return True
        return False

    def rsi_has_crossed_down_fifty_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        prev = df['rsi'][index - 1]
        curr = df['rsi'][index]
        if prev < 50 and curr > 50 and abs(curr - prev) >= self.params.fifty_cross_diff:
            return True
        return False

    def rsi_has_crossed_up_fifty_threshold(self, index):
        df = self.get_df()
        if index == 0 or np.isnan(df['rsi'][index]):
            return False
        prev = df['rsi'][index - 1]
        curr = df['rsi'][index]
        if prev > 50 and curr < 50 and abs(curr - prev) >= self.params.fifty_cross_diff:
            return True
        return False

    def generate_strategy_signal(self, i):

        df = self.get_df()
        buy_signal = False
        sell_signal = False

        if self.params.entry_signal == 'enter_threshold':
            if self.rsi_enter_lower_threshold(i):
                buy_signal = True
            if self.rsi_enter_upper_threshold(i):
                sell_signal = True

        elif self.params.entry_signal == 'exit_threshold':
            if self.rsi_exit_lower_threshold(i):
                buy_signal = True
            if self.rsi_exit_upper_threshold(i):
                sell_signal = True

        elif self.params.entry_signal == 'max_in_threshold':
            raise Exception(
                "Entry Signal handler not implemented: max_in_threshold")

        elif self.params.entry_signal == 'strong_fifty_cross':
            if self.rsi_has_crossed_up_fifty_threshold(i):
                buy_signal = True
            if self.rsi_has_crossed_down_fifty_threshold(i):
                sell_signal = True
        else:
            raise Exception(
                "Unexpected entry signal parameter: " + self.params.entry_signal)

        if buy_signal == sell_signal:
            assert(buy_signal == False)

        if buy_signal:
            df['long'][i] = df['Perc Var'][i]

        if sell_signal:
            df['short'][i] = df['Perc Var'][i]

        return buy_signal, sell_signal

    def get_rsi_band(self, value):
        if value < self.params.lower_threshold:
            return 'lower_band'
        if value > self.params.upper_threshold:
            return 'upper_band'
        return 'none'
        

    def simulate(self, stock):

        log.debug("Running simulation on " + stock)
        i = 0
        in_position = False
        df = self.get_df()
        start = df['Perc Var'][0]
        liquidate_threshold = 0
        reset_threshold = 0
        position = ""
        market_closing_soon = False

        close_price = df['close'][0]
        if self.value_close_to_threshold(close_price) == 0:
            log.debug("Skipping " + stock +
                      " as it's too expensive " + str(close_price))
            return False

        self.init_helper_dataframes()

        threshold_reset = 0
        buy_signal = False
        sell_signal = False
        self.set_scale_target(0.5)
        self.set_stop_loss(0.25)
        first_valid_rsi_sample = True
        start_band = None
        current_band = None
        in_band_count = 0

        for el in df['Perc Var']:

            # if len(dataframe['close']) - i <= self.params["sell_before_market_closes"]:
            if len(df['close']) - i <= 10:
                market_closing_soon = True

            # No rsi data available
            if np.isnan(df['rsi'][i]):
                i += 1
                continue

            buy_signal = sell_signal = False

            # We generate a buy/sell signal if we have a certain number of samples within
            # the initial rsi band
            if first_valid_rsi_sample:
                start_band = self.get_rsi_band(df['rsi'][i])
                first_valid_rsi_sample = False
                if start_band == 'upper_band' or start_band == 'lower_band':
                    in_band_count += 1
                i += 1
                continue
            else:
                current_band = self.get_rsi_band(df['rsi'][i])
                if current_band == start_band and in_band_count != -1:
                    in_band_count += 1                    
                else:
                    in_band_count = -1

            if in_band_count != -1:
                if in_band_count == self.params.upfront_samples:
                    if start_band == 'upper_band':
                        buy_signal = True
                    else: 
                        sell_signal = True
                elif in_band_count > self.params.upfront_samples:
                    in_band_count = -1
            else:
                buy_signal, sell_signal = self.generate_strategy_signal(i)
            time = df['time'][i]
            close = df['close'][i]

            if buy_signal is True:
                df['rsi_buy'][i] = df['rsi'][i]

            if sell_signal is True:
                df['rsi_sell'][i] = df['rsi'][i]

            if not self.in_position() and not market_closing_soon:
                if buy_signal is True:
                    self.long(stock, close, time, i)
                    self.enter_position("long")

                if sell_signal is True:
                    self.short(stock, close, time, i)
                    self.enter_position("short")

            elif self.in_position() and not market_closing_soon:

                # if buy_signal is True:
                #     log.warn("Ignoring buy signal becaseu we are already in position")
                # if sell_signal is True:
                #     log.warn("Ignoring sell signal becaseu we are already in position")

                position_info = self.get_position_info(stock, close)

                if self.hit_target(stock, close):
                    self.scale_trade()
                elif self.hit_loss(stock, close):
                    self.liquidate(stock, close, time)
                    self.exit_position()

                # if buy_signal or sell_signal:
                #     self.liquidate(stock, cloe, time)
                #     dataframe['liq'][i-1] = dataframe['Perc Var'][i]
                #     if buy_signal:
                #         self.long(stock, close, time)
                #     elif sell_signal:
                #         self.short(stock, close, time)

                #     buy_signal = False
                #     sell_signal = False

            elif self.in_position() and market_closing_soon:
                buy_signal = False
                sell_signal = False
                self.liquidate(stock, close, time)
                self.exit_position()

            i += 1

        return True

    def run_strategy(self, api):

        try:
            symbols = self.get_symbols()
            used_stocks = []

            gains = {}

            base_data_dir = self.get_bars_data_folder()

            # log.info("Strategy RSI on with" + str(self.params.params))

            result_array = []

            period = str(self.params.rsi_indicator.period)
            threshold = str(self.params.upper_threshold)
            mean_type = str(self.params.rsi_indicator.mean_type)
            mean_period = str(self.params.rsi_indicator.mean_period)

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

                df['Perc Var'] = (df['close'] - df['close']
                                  [0])/df['close'][0] * 100
                self.set_df(df)
                rsfld = self.results_folder + "/" + s + ".png"

                success = self.simulate(s)
                if not success:
                    continue

                gains[s] = (self.current_capital - self.start_capital)

                fig, ax = plt.subplots()
                df['Perc Var'].plot(grid=True,
                                    title=s + " profit: " + str(gains[s]),
                                    legend=True,
                                    label='Percentage Variation',
                                    ax=ax,
                                    figure=fig,
                                    figsize=(12, 8))
                # df[self.ma_slow_str].plot(grid=True,
                #                           legend=True,
                #                           color="purple",
                #                           alpha=0.7,
                #                           label=self.ma_slow_str,
                #                           ax=ax,
                #                           figure=fig)
                # df[self.ma_fast_str].plot(grid=True,
                #                           legend=True,
                #                           color="orange",
                #                           alpha=0.7,
                #                           label=self.ma_fast_str,
                #                           ax=ax,
                #                           figure=fig)
                df['long'].plot(grid=True,
                                legend=True,
                                marker="^",
                                color="green",
                                ax=ax,
                                figure=fig)
                df['short'].plot(grid=True,
                                 legend=True,
                                 marker="v",
                                 color="red",
                                 ax=ax,
                                 figure=fig)
                df['liq'].plot(grid=True,
                               legend=True,
                               marker="o",
                               color="orange",
                               ax=ax,
                               figure=fig)
                fig.savefig(rsfld)
                plt.close(fig)
                plt.clf()

                fig, ax = plt.subplots()

                df['rsi'].plot(grid=True,
                               legend=True,
                               color="purple",
                               ax=ax,
                               figure=fig,
                               marker='x',
                               figsize=(12, 8))
                df['rsi_buy'].plot(grid=True,
                                   legend=True,
                                   color="green",
                                   ax=ax,
                                   figure=fig,
                                   label='buy signals',
                                   marker='^')
                df['rsi_sell'].plot(grid=True,
                                    legend=True,
                                    color="red",
                                    ax=ax,
                                    figure=fig,
                                    label='sell signals',
                                    marker='v')
                ax.axhline(y=self.params.upper_threshold, xmin=-1,
                           xmax=1, color='green', linestyle='--', lw=2)
                ax.axhline(y=self.params.lower_threshold, xmin=-1,
                           xmax=1, color='orange', linestyle='--', lw=2)
                rsfld = self.results_folder + "/" + s + "_rsi.png"
                fig.savefig(rsfld)
                plt.close(fig)

                

            # print("Total gain for " + s + " = " +
            #      str(self.current_capital - self.start_capital))
            #gains[s] = (self.current_capital - self.start_capital)

            total_gain = 0.0
            for s in gains:
                # log.info("Total gain for " + s + " = " + str(gains[s]) + "$")
                total_gain += gains[s]

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

                #print(stock + " profit: " + str(per_stock_gain))
                #print("  good: " + str(good_trades))
                #print("  bad : " + str(bad_trades))
                result_array.append({
                "strategy": "rsi",
                "period": str(period),
                "mean_type": str(mean_type),
                "mean_period": str(mean_period),
                "threshold": str(threshold),
                "stock": stock,
                "gain": total_gain
            })
            #print('Overall Total Gain: ' + str(total_gain))

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

            result_array.append({
                "strategy": "rsi",
                "date": str(self.get_date_string()),
                "period": str(period),
                "mean_type": str(mean_type),
                "mean_period": str(mean_period),
                "threshold": str(threshold),
                "stock": "TOTAL",
                "gain": total_gain
            })
            return result_array
            

        except Exception as e:
            log.error("Got exception " + str(e))
            traceback.print_tb(e.__traceback__)

        # self.store_transactions()
        # time.sleep(2)

    def set_generated_param(self, params):

        rsi_strategy_params = RSIStrategyParams()
        # rsi_strategy_params.set_period(params['period'])
        rsi_strategy_params.set_entry_signal(params['entry_signal'])
        rsi_strategy_params.set_limit_threshols(params['limit_threshold'])

        rsi_indicator_params = RSIIndicator(
            params['rsi_period'],
            params['rsi_mean_period'],
            params['mean_type'],
            params['source']
        )
        rsi_strategy_params.set_rsi_indicator(rsi_indicator_params)
        self.params = rsi_strategy_params

        self.results_folder += (
            'peri-' + str(params['rsi_period']) + "_"
            'meanperi-' + str(params['rsi_mean_period']) + "_"
            'meantype-' + str(params['mean_type']) + "_"
            'entry-' + str(params['entry_signal']) + "_"
            'thr-' + str(params['limit_threshold']) + "/"
        )

        log.debug("Params: " + str(params))

        os.makedirs(self.results_folder)

    def generate_param_combination(self,size):

        if size == 'full':
            # RSI Indicator Parameters
            rsi_period = [6,7,8,9,10,11,12,13,14]
            rsi_mean_period = [4,5,6,7,8,9,10]
            mean_type = ['SMA','EMA']
            source = ['close']

            # RSI Strategy Parameters
            limit_threshold = [20,21,27,28,29,30,31,32]
            entry_signal = [
                # 'enter_threshold'
                'exit_threshold'
                # 'strong_fifty_cross'
            ]

        elif size == 'medium':
            # RSI Indicator Parameters
            rsi_period = [6,7,8,9,10,11,12,13,14]
            rsi_mean_period = [4,5,6,7,8,9,10]
            mean_type = ['SMA','EMA']
            source = ['close']

            # RSI Strategy Parameters
            limit_threshold = [20,21,27,28,29,30,31,32]
            entry_signal = [
                # 'enter_threshold'
                'exit_threshold'
                # 'strong_fifty_cross'
            ]

        elif size == 'small':
            # RSI Indicator Parameters
            rsi_period = [6,7]
            rsi_mean_period = [4,6]
            mean_type = ['SMA','EMA']
            source = ['close']

            # RSI Strategy Parameters
            limit_threshold = [30,32]
            entry_signal = [
                # 'enter_threshold'
                'exit_threshold'
                # 'strong_fifty_cross'
            ]

        else:
            raise Exception("Unrecognised size")

        # All params needed for the strategy to run, included the indicator
        # limit_threshold = range(8, 10, 2)
        # period = range(14, 15)
        # mean_type = ['EMA']
        # source = ['close']
        # entry_signal = [
        #     'exit_threshold'
        # ]
        # fifty_cross_diff = [10]

        
        fifty_cross_diff = [10]

        param_product = itertools.product(
            limit_threshold,
            rsi_period,
            rsi_mean_period,
            mean_type,
            source,
            entry_signal,
            fifty_cross_diff
        )

        params = []
        for param in param_product:
            if param[1] >= param[2]:
                params.append({
                    'limit_threshold': param[0],
                    'rsi_period': param[1],
                    'rsi_mean_period': param[2],
                    'mean_type': param[3],
                    'source': param[4],
                    'entry_signal': param[5],
                    'fifty_cross_diff': param[6]
                })

        return params

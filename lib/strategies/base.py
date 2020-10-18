import os
import operator
import datetime
import pandas as pd
import datetime as dt
import multiprocessing as mp
import matplotlib.pyplot as plt
# import lib.trading.generic as capital_managment

import lib.util.logger as logger
logger.setup_logging("BaseStrategy")
log = logger.logging.getLogger("BaseStrategy")

backtesting_results = []
results_reported = 0
total_results = 0
perc = range(0, 102)


def collect_result(result):
    global perc
    global total_results
    global results_reported
    global backtesting_results

    results_reported += 1
    if result is None:
        log.error("No results found")
        return

    backtesting_results.append(result)

    while float(results_reported) / float(total_results) * 100.0 >= perc[0]:
        log.debug("{}% of the simulations completed {}".format(
            perc[0],
            results_reported
        ))
        if len(perc) > 1:
            perc = perc[1:]


class BacktestStrategy():

    def print_backtest_csv_format(self, results_folder):
        global backtesting_results

        f = open(results_folder + "stats.csv", "w")
        f.write(self.strategy_params_to_csv_header(
            backtesting_results[0]) + "\n")
        for element in backtesting_results:
            f.write(self.strategy_params_to_csv_line(element) + "\n")

    def print_backtest_profits(self):

        for result in backtesting_results:
            total_profit = 0
            for symbol in result:
                stock_profit = 0
                for position in result[symbol]:
                    profit = position.get_profit()
                    log.debug("{:8s} profit: {:.2f}$".format(
                        symbol+"'s",
                        profit))
                    stock_profit += profit
                log.info("Total {} profit: {:.2f}$".format(symbol, stock_profit))
                total_profit += stock_profit
            log.info("Total profit: {:.2f}$".format(total_profit))

    def print_trade_stats(self):
        for result in backtesting_results:
            winners = 0
            losers = 0
            for symbol in result:
                for position in result[symbol]:
                    profit = position.get_profit()
                    if profit > 0:
                        winners += 1
                    else:
                        losers += 1
                # log.info("Total {} profit: {}".format(symbol, stock_profit))

            log.info("Total winners: {} ({:.2f}%)".format(winners, winners/(winners+losers)))
            log.info("Total losers: {} ({:.2f}%)".format(losers, losers/(winners+losers)))

    def profits_to_dataframe(self):
        df = pd.DataFrame(columns=['date', 'symbol', 'profit', "total"])
        total_profit = 0.0
        for result in backtesting_results:
            for symbol in result:
                for position in result[symbol]:
                    profit = position.get_profit()
                    last_trade = position.get_trades()[-1]
                    total_profit += profit
                    df = df.append({
                        "date": last_trade.date,
                        "symbol": last_trade.symbol,
                        "profit": profit
                    }, ignore_index=True)
        df = df.set_index("date")
        df.sort_index(inplace=True)
        df["total"] = df["profit"].cumsum()
        df["total"].plot()
        plt.grid()
        plt.show()

    def trades_to_dataframe(self):
        df = pd.DataFrame(columns=['date', 'capital', 'max'])
        for result in backtesting_results:
            for symbol in result:
                for position in result[symbol]:
                    for trade in position.get_trades():
                        if (position.side == "long" and trade.side == "buy" or
                                position.side == "short" and trade.side == "sell"):
                            traded_capital = -abs(trade.quantity * trade.price)
                        else:
                            traded_capital = abs(trade.quantity * trade.price)
                        df = df.append({
                            "date": trade.date,
                            "capital": -traded_capital
                        }, ignore_index=True)
        df = df.set_index("date")
        df.sort_index(inplace=True)
        max_capital_invested = 0.0
        log.info("Max capital invested {}$".format(max_capital_invested))
        df["max"] = df["capital"].cumsum()
        df["max"].plot()
        plt.grid()
        plt.show()

    def stringify_strategy_params(self, params):
        param_string = params['strategy'] + "("
        for elem in params:
            if elem != "strategy" and elem != "gain":
                param_string += elem + "=" + str(params[elem]) + ","
        param_string = param_string[:-1]
        param_string += ")"
        return param_string

    def strategy_params_to_csv_header(self, params):
        params_header = ""
        for elem in params:
            params_header += elem + ","
        return params_header[:-1]

    def strategy_params_to_csv_line(self, params):
        params_values = ""
        for elem in params:
            params_values += str(params[elem]) + ","
        return params_values[:-1]

    def create_barchart_for_results(self, result_folders, filter):
        for date in result_folders:
            backtesting_dict = dict()
            for res in backtesting_results:
                if res['stock'] == filter and res['date'] == date:
                    key_param_string = self.stringify_strategy_params(res)
                    backtesting_dict[key_param_string] = float(res['gain'])

            # Sorting the dictionary
            backtesting_dict_sorted = dict(
                sorted(backtesting_dict.items(), key=operator.itemgetter(1), reverse=True))
            profit_df = pd.DataFrame({
                'strategy': list(backtesting_dict_sorted.keys()),
                'gain': list(backtesting_dict_sorted.values())
            })

            # Plot a chart that tells us how our strategy performed based on different
            # params as input
            fig, ax = plt.subplots()
            profit_file_name = result_folders[date] + "/strategy_results.png"
            profit_df.plot.bar(title='Strategy Performance', x='strategy',
                               y='gain', rot=90, ax=ax, figure=fig, grid=True, figsize=(40, 10))
            fig.savefig(profit_file_name)
            plt.close(fig)

            for elem in backtesting_dict_sorted:
                print(elem + ": " + str(backtesting_dict_sorted[elem]) + "$")

    def run(self, api, strategy_class, pool_size):

        global total_results
        now = dt.datetime.now()
        pool = mp.Pool(pool_size)

        days = ["08"]
        month = "09"
        year = "2020"

        dates = []
        result_folders = {}

        for day in days:
            strategy = strategy_class()
            strategy.set_day(day)
            strategy.set_month(month)
            strategy.set_year(year)
            dates.append(strategy.get_date_string())
            strategy.set_api(api)
            strategy.pull_stock_info()
            param_comb = strategy.generate_param_combination('single')
            result_folder = strategy.result_folder + "/" + \
                str(now)[:19] + "/" + strategy.get_date_string() + "/"
            os.makedirs(result_folder)
            result_folders[strategy.get_date_string()] = result_folder

            total_results += len(param_comb)
            log.info("Total number of simulations = " + str(total_results))

            for param_set in param_comb:
                log.info("Param set: " + str(param_set))
                strategy = strategy_class()
                strategy.results_folder = result_folder
                strategy.set_generated_param(param_set)
                strategy.set_day(day)
                strategy.set_month(month)
                strategy.set_year(year)
                strategy.set_api(api)

                pool.apply_async(strategy.run_strategy, callback=collect_result)
                # pool.apply_async(strategy.run_strategy, args=[
                #     api], callback=collect_result)

        pool.close()
        pool.join()
        if len(backtesting_results) == 0:
            log.critical("No results generated by simulation")
            return

        self.print_backtest_profits()

        self.print_trade_stats()

        self.profits_to_dataframe()

        self.trades_to_dataframe()

        # self.print_backtest_csv_format(result_folder)

        # self.create_barchart_for_results(result_folders, "TOTAL")

        # Here we want to get some other results like min, max, avg and stddev

    """
    Runs the backtesting for a specific set of inputs you need to select

    Parameters
    ----------
    - strategy_class: type
        One of the strategies available in lib.strategies
    - trading_type: str
        Intra-day or multy-days (note that intra-day will force closing all your position by EOD)
    - datetime_start: datetime
        The beginning of the time frame for the simulation
    - datetime_end: datetime
        The end of the time frame for the simulation
    - param_size: str
        The strategy and indicators will be generating possible combinations of parameters, the
        size of these combinations will be default, light, medium, full
    - indicator_list: list
        A list of indicators to use with the strategy, these will be used by the strategy which
        should know which indicators to use and how
    - parallel_processes: int
        Number of parallel processes to run for the simulation to use. A good number (considering m
        to be the number of cores available on the platfrom) will be between m and m*2 depending on
        the stress you want to put on your machine

    Returns
    -------
    list
        a list of strings used that are the header columns
    """

    def run_new(self,
                symbols: str,
                strategy_class: type,
                param_size: str,
                indicator_list: list,
                datetime_start: datetime,
                datetime_end: datetime,
                trading_type: str,
                pool_size: int):

        global total_results
        now = dt.datetime.now()
        pool = mp.Pool(pool_size)

        days = ["08"]
        month = "09"
        year = "2020"

        dates = []
        result_folders = {}

        for day in days:
            strategy = strategy_class()
            strategy.set_day(day)
            strategy.set_month(month)
            strategy.set_year(year)
            dates.append(strategy.get_date_string())
            # strategy.set_api(api)
            strategy.pull_stock_info()
            param_comb = strategy.generate_param_combination('single')
            result_folder = strategy.result_folder + "/" + \
                str(now)[:19] + "/" + strategy.get_date_string() + "/"
            os.makedirs(result_folder)
            result_folders[strategy.get_date_string()] = result_folder

            total_results += len(param_comb)
            log.info("Total number of simulations = " + str(total_results))

            for param_set in param_comb:
                log.info("Param set: " + str(param_set))
                strategy = strategy_class()
                strategy.results_folder = result_folder
                strategy.set_generated_param(param_set)
                strategy.set_day(day)
                strategy.set_month(month)
                strategy.set_year(year)
                # strategy.set_api(api)

                pool.apply_async(strategy.run_strategy, callback=collect_result)

        pool.close()
        pool.join()
        if len(backtesting_results) == 0:
            log.critical("No results generated by simulation")
            return

        log.info("Simulations completed, storing results now")

        self.print_backtest_profits()


class StockMarketStrategy():

    def __init__(self):
        self.name: str = None
        self.description: str = None
        self.day: str = None
        self.month: str = None
        self.year: str = None
        self.api = None
        self.transactions = dict()
        self.current_positions = dict()
        self.position = None
        self.trade_scaled = 0
        self.main_df = None

        self.indicators = list()

    def set_api(self, api):
        self.api = api

    def get_api(self):
        return self.api

    def get_current_positions(self):
        return self.current_positions

    def in_position(self):
        if self.position == 'long' or self.position == 'short':
            return True
        return False

    def hit_target(self, stock, close_price):
        if self.in_position():
            position_info = self.get_position_info(stock, close_price)
            perc_pl = position_info['perc pl']
            if perc_pl > self.scale_target:
                log.debug('Hit target ' + str(close_price) +
                          "$" + " (" + str(perc_pl) + ")")
                return True
            return False
        return False

    def hit_loss(self, stock, close_price):
        if self.in_position():
            position_info = self.get_position_info(stock, close_price)
            perc_pl = position_info['perc pl']
            if perc_pl < self.stop_loss:
                log.debug('Hit stop loss ' + str(close_price) +
                          "$" + " (" + str(perc_pl) + ")")
                return True
            return False
        return False

    def scale_trade(self):
        self.scale_target += 0.25
        if self.trade_scaled > 0:
            self.stop_loss += 0.25
        else:
            self.stop_loss += 0.55

        self.trade_scaled += 1
        log.debug('Scaling trade ' + str(self.scale_target) +
                  "$" + " (" + str(self.stop_loss) + ")")

    def enter_position(self, position):
        if position == 'long' or position == 'short':
            self.position = position
        else:
            raise Exception("Unknown position " + position)

    def exit_position(self):
        if self.position == 'long' or self.position == 'short':
            self.position = None
            self.set_stop_loss(1.0)
            self.set_scale_target(0.5)
        else:
            raise Exception("Unknown position " + self.position)

    def set_stop_loss(self, perc_val):
        self.stop_loss = -perc_val
        self.trade_scaled = 0

    def set_scale_target(self, perc_val):
        self.scale_target = perc_val

    def get_transactions(self):
        return self.transactions

    def set_day(self, day):
        self.day = day

    def set_month(self, month):
        self.month = month

    def set_year(self, year):
        self.year = year

    def get_day(self):
        return self.day

    def get_month(self):
        return self.month

    def get_year(self):
        return self.year

    def get_date_string(self):
        return self.year + "-" + self.month + "-" + self.day

    def get_bars_data_folder(self):
        if (self.day is None or self.month is None or self.year is None):
            raise Exception("One of the datetime parameters is None")
        return ("data/minute_charts/" + self.year + "-" + self.month + "-" + self.day + "/")

    def tick_within_market_hours(self, tick):
        if (tick.day == int(self.day) and
            tick.month == int(self.month) and
            ((tick.hour == 9 and tick.minute >= 30) or
             (tick.hour >= 10 and tick.hour < 16) or tick.hour == 16 and tick.minute == 0)):
            return True
        return False

    def build_dataframe(self, barset, symbol):
        lows = []
        times = []
        opens = []
        highs = []
        closes = []
        volumes = []

        for elem in barset:
            for bar in barset[elem]:

                curr_time = bar.t
                print(bar.t)

                if self.tick_within_market_hours(curr_time):
                    times.append(str(bar.t))
                    opens.append(float(bar.o))
                    closes.append(float(bar.c))
                    highs.append(float(bar.h))
                    lows.append(float(bar.l))
                    volumes.append(float(bar.v))

        # df = pd.DataFrame(None, pd.DatetimeIndex(pd.Timestamp(times)), {
        #     'time': times,
        #     'open': opens,
        #     'close': closes,
        #     'high': highs,
        #     'low': lows,
        #     'volume': volumes
        # })

        df = pd.DataFrame({
            'time': times,
            'open': opens,
            'close': closes,
            'high': highs,
            'low': lows,
            'volume': volumes
        })

        date = self.year + "-"
        date += self.month + "-"
        date += self.day

        base_dir = 'data/minute_charts/'

        if not os.path.exists(base_dir + date + '/'):
            os.makedirs(base_dir + date + '/')

        df.to_csv(base_dir + date + '/' + symbol + '.csv')

        self.set_df(df)

    def get_df(self):
        return self.main_df

    def set_df(self, dataframe):
        self.main_df = dataframe

    def get_symbols(self):
        return ['AAPL', 'INTC']

    def get_position_info(self, stock, curr_val):
        if not self.in_position():
            raise Exception("Not in position")
        quantity = self.current_positions[stock]['quantity']
        val = self.current_positions[stock]['value']
        cost_basis = abs(quantity) * val
        market_value = abs(quantity) * curr_val

        if quantity > 0:
            total_pl = (market_value - cost_basis)
            perc_pl = (market_value - cost_basis) / cost_basis * 100.0
        elif quantity < 0:
            total_pl = (cost_basis - market_value)
            perc_pl = (cost_basis - market_value) / cost_basis * 100.0

        return {
            'stock': stock,
            'quantity': quantity,
            'current value': curr_val,
            'price': val,
            'cost': cost_basis,
            'market value': market_value,
            'total pl': total_pl,
            'perc pl': perc_pl
        }

    def short(self, stock, value, time, i):
        quant = self.value_close_to_threshold(value)
        self.main_df['short'][i] = self.main_df['Perc Var'][i]
        if stock not in self.current_positions:
            log.debug("Opening short position for " +
                      str(int(quant)) + " " + stock + " stocks at " + "{:.2f}".format(value))
            self.current_positions[stock] = {
                "quantity": -quant,
                "value": value,
                "direction": "short"
            }
            self.current_capital -= (value * -quant)
            transactions = self.get_transactions()
            if stock not in transactions:
                transactions[stock] = []
            transactions[stock].append({
                "type": "short",
                "time": time,
                "quantity": -quant,
                "price": value,
                "value": value
            })

    def long(self, stock, value, time, i):
        quant = self.value_close_to_threshold(value)
        self.main_df['long'][i] = self.main_df['Perc Var'][i]
        if stock not in self.current_positions:
            log.debug("Opening long position for " +
                      str(int(quant)) + " " + stock + " stocks at " + "{:.2f}".format(value))
            self.current_positions[stock] = {
                "quantity": quant,
                "value": value,
                "direction": "long"
            }
            self.current_capital -= (value * quant)
            transactions = self.get_transactions()
            if stock not in transactions:
                transactions[stock] = []
            transactions[stock].append({
                "type": "long",
                "time": time,
                "quantity": quant,
                "price": value
            })
        else:
            raise Exception("Cannot enter a position already in one")

    def liquidate(self, stock, value, time):
        if stock in self.current_positions:
            current_position = self.current_positions[stock]
            # print("Start equity is " + str(self.current_capital))
            profit = (
                value - current_position["value"]) * float(current_position["quantity"])
            # print("Profit for this trade is: " + str(profit))
            self.current_capital += value * \
                float(current_position["quantity"])
            # print("Updated equity is " + str(self.current_capital))
            # print("")
            direction = current_position["direction"]
            log.debug("Liquidate " + direction + " position " +
                      str(int(current_position["quantity"])) + " stocks at " +
                      "{:.2f}".format(value) + " and profit " + str(profit))
            if direction == "long":
                if value > current_position["value"]:
                    assert(profit > 0)
                if value < current_position["value"]:
                    assert(profit < 0)

            if direction == "short":
                if value < current_position["value"]:
                    assert(profit > 0)
                if value > current_position["value"]:
                    assert(profit < 0)

            if stock not in self.profits:
                self.profits[stock] = [profit]
            else:
                self.profits[stock].append(profit)
            transactions = self.get_transactions()
            transactions[stock].append({
                "type": "liquidate",
                "time": time,
                "quantity": int(current_position["quantity"]),
                "value": value
            })

            del self.current_positions[stock]

    def value_close_to_threshold(self, value):
        rem = round(self.get_per_trade_budget() / value)

        if rem * value > (self.get_per_trade_budget() * 1.1):
            return rem - 1
        return rem

    def get_per_trade_budget(self):
        return 1000

    def simulate(self):
        pass

    def run_live(self):
        pass

    def generate_param_combination(self):
        pass

    def store_transactions(self):
        try:
            for stock in self.transactions:
                # print(stock + "'s transactions")
                index = 0
                total_profit = 0.0
                for trans in self.transactions[stock]:
                    # print(trans,end="")
                    if trans['type'] == 'liquidate':
                        curr_value = trans['value']
                        prev_value = self.transactions[stock][index-1]['value']
                        quantity = self.transactions[stock][index -
                                                            1]['quantity']
                        if self.transactions[stock][index-1]['type'] == 'long':
                            profit = (curr_value - prev_value) * abs(quantity)
                            # print(" Profit: " + str(profit))
                            total_profit += profit
                        elif self.transactions[stock][index-1]['type'] == 'short':
                            profit = (prev_value - curr_value) * abs(quantity)
                            # print(" Profit: " + str(profit))
                            total_profit += profit

                    # else:
                        # print("")

                    index += 1

        except Exception as e:
            print(e)

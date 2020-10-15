''' 
This module is responsible to provide an entry point on the portfolio and 
manage the api around it
'''

import json
import time
import datetime
import api_proxy

import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt import risk_models
from pypfopt import expected_returns
from lib.trading.alpaca import AlpacaTrading
from pandas_datareader import data as web
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

plt.style.use('fivethirtyeight')

paper_account = api_proxy.TradeApiProxy("paper")
paper_account2 = api_proxy.TradeApiProxy("paper2")


class Portfolio():

    def __init__(self):
        f = open("data/investments.json", "r")
        self.investments = json.load(f)
        f.close()

    def get_capital_invested_in(self, symbol):
        capital_invested = 0.0

        if symbol in self.investments:
            for investment in self.investments[symbol]["investments"]:
                capital_invested += float(investment["shares"]) * \
                    float(investment["value"])

        return capital_invested

    def get_number_of_share_for(self, symbol):
        total_shares = 0.0

        if symbol in self.investments:
            for investment in self.investments[symbol]["investments"]:
                total_shares += float(investment["shares"])

        return total_shares

    def get_cost_for(self, symbol):
        total_cost = 0.0

        if symbol in self.investments:
            for investment in self.investments[symbol]["investments"]:
                total_cost += float(investment["shares"]) * \
                    float(investment["value"]) + 1.26

        return total_cost

    def get_total_cost(self):
        total_cost = 0.0

        for symbol in self.get_assets_invested():
            total_cost += self.get_cost_for(symbol)

        return total_cost

    def get_total_invested(self):
        total_invested = 0.0

        for symbol in self.get_assets_invested():
            total_invested += self.get_capital_invested_in(symbol)

        return total_invested

    def get_assets_invested(self):
        return self.investments.keys()


p = Portfolio()


def main_print_loop():

    times = []
    latest_quotes = {}
    perc_diff = {}

    while True:
        now = datetime.datetime.now()
        times.append(now)

        for stock in p.get_assets_invested():
            close_price = paper_account.get_limit_minute_barset(stock, limit=2)[
                stock][-1].c
            if stock not in latest_quotes:
                latest_quotes[stock] = [close_price]
            else:
                latest_quotes[stock].append(close_price)

            market_value = close_price * p.get_number_of_share_for(stock)
            original_cost = p.get_cost_for(stock)
            #print(stock + " marked value " + "{:.2f}".format(market_value))
            #print(stock + " original cost " + "{:.2f}".format(original_cost))
            perc = (market_value - original_cost)

            if stock not in perc_diff:
                perc_diff[stock] = [perc]
            else:
                perc_diff[stock].append(perc)

        dataframe = pd.DataFrame(None, pd.DatetimeIndex(times), None)
        for stock in p.get_assets_invested():
            dataframe[stock] = np.array(perc_diff[stock])
            dataframe[stock].plot(
                label=stock, figsize=(15, 10), title='Return')

        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.grid()
        plt.draw()
        #mng = plt.get_current_fig_manager()
        # mng.frame.Maximize(True)
        plt.pause(0.005)

        time.sleep(get_polling_rate_sec(now))
        plt.clf()

    stock = 'FB'
    for i in paper_account.get_limit_minute_barset(stock, limit=10)[stock]:
        print(i)


def get_polling_rate_sec(now):

    market_open = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=14, minute=30)
    half_hour_before_market_open = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=14, minute=00)
    hour_after_market_open = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=15, minute=30)
    hour_before_market_closes = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=20, minute=00)
    market_closed = datetime.datetime(
        year=now.year, month=now.month, day=now.day, hour=21, minute=00)

    print("\nTime of the update is " + str(now))

    if now < half_hour_before_market_open:
        print("< half_hour_before_market_open")
        return 5 * 60
    elif half_hour_before_market_open < now < market_open:
        print("half_hour_before_market_open < now < market_open")
        return 2 * 60
    elif market_open < now < hour_after_market_open:
        print("market_open < now < hour_after_market_open")
        return 15
    elif hour_after_market_open < now < hour_before_market_closes:
        print("hour_after_market_open  < now < hour_before_market_closes")
        return 60
    elif hour_before_market_closes < now < market_closed:
        print("hour_before_market_closes < now < market_closed")
        return 15
    elif market_closed < now:
        print("market_closed < now")
        return 5 * 60
    else:
        return 60


def get_stocks_in_watchlist():

    watch_lists = paper_account.api.get_watchlists()
    primary_watch_list = paper_account.api.get_watchlist(watch_lists[0].id)
    return primary_watch_list


def get_weights(watchlist):

    wl_len = len(watchlist)
    base_weight = float("{:.5f}".format(1.0/wl_len))
    weights = []
    for i in range(0, wl_len-1):
        weights.append(base_weight)
    weights.append(1.0 - (base_weight*(wl_len-1)))
    stock_weights = np.array(weights)
    print(stock_weights)
    sum = 0.0
    for el in stock_weights:
        sum += el
    print("Sum is " + str(sum))
    return stock_weights


def build_stock_weghts(stock_info):

    weights = []
    for stock in stock_info:
        if stock["shortable"] is True:
            weights.append((-1, 1))
        else:
            weights.append((0, 1))
    return weights


if __name__ == "__main__":

    wl = get_stocks_in_watchlist()

    watchlist = []
    for e in wl.assets:
        watchlist.append(e)

    shortable_info = []
    for stock in watchlist:
        print(stock["symbol"] + " " + str(stock["shortable"]))
        shortable_info.append({
            "stock": stock["symbol"],
            "shortable": stock["shortable"]
        })

    print("You have " + str(len(watchlist)) + " in your portfolio")

    weights = get_weights(watchlist)

    stock_start = '2015-01-01'
    #stock_end = '2020-07-02'
    stock_end = datetime.datetime.today().strftime("%Y-%m-%d")

    # Create a dataframe to store the adjusted stock price of the stocks
    df = pd.DataFrame()
    for stock in watchlist:
        print("Fetching data for " + stock["symbol"] + "...", end="")
        df[stock["symbol"]] = web.DataReader(
            stock["symbol"], data_source='yahoo', start=stock_start, end=stock_end)['Adj Close']
        print("DONE")

    print(df)
    for stock in watchlist:
        symbol = stock["symbol"]
        print(symbol + ": " + str(df[symbol][len(df[symbol])-1]))

    # Show the simple daily returns
    returns = df.pct_change()

    initial_capital = 31300

    # Create the annualised covariance matrix
    annual_covariance_matrix = returns.cov() * 252
    port_variance = np.dot(weights.T, np.dot(
        annual_covariance_matrix, weights))
    port_volatility = np.sqrt(port_variance)
    port_annual_return = np.sum(returns.mean() * weights) * 252
    print("Plain portfolio variance       : " + str(port_variance))
    print("Plain portfolio volatility     : " + str(port_volatility))
    print("Plain portfolio ann return (%) : {:.2f} ".format(
        port_annual_return*100))
    print("Plain portfolio ann return ($) : {:.2f} ".format(
        (1+port_annual_return)*initial_capital))

    print("Not bad!! Let's try to optimise it")
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)
    ef = EfficientFrontier(
        mu, S, weight_bounds=build_stock_weghts(shortable_info))

    print("Max sharpe ratio -----------------------------------------------------------------")
    weights2 = ef.max_sharpe()
    clean_weitghs2 = ef.clean_weights()
    print("Raw weights: ")
    print(weights2)
    print("Clean weights: ")
    print(clean_weitghs2)
    ef.portfolio_performance(verbose=True)

    print("Lower risks ----------------------------------------------------------------------")
    weights3 = ef.min_volatility()
    clean_weitghs3 = ef.clean_weights()
    print("Raw weights: ")
    print(weights3)
    print("Clean weights: ")
    print(clean_weitghs3)
    ef.portfolio_performance(verbose=True)

    latest_prices = get_latest_prices(df)
    clean_weitghs3

    da = DiscreteAllocation(clean_weitghs3, latest_prices,
                            total_portfolio_value=initial_capital)
    allocation, leftover = da.lp_portfolio()
    print("========= Allocation =========")
    print(allocation)
    print("========== Leftover ==========")
    print(leftover)

    value = 0.0
    sorted_allocation = collections.OrderedDict(sorted(allocation.items()))
    positions = proxy.api.list_positions()
    for k, v in sorted_allocation.items():
        alloc = int(v)
        stock_curr_value = df[k][len(df[k])-1]
        stock_value = abs(stock_curr_value * alloc)
        print(k + " " + str(alloc) + " " + str(stock_value))
        value += stock_value

        found = False
        side = None
        qty = None
        stock = k
        for pos in positions:
            if pos.symbol == k:
                found = True
                side = pos.side
                qty = float(pos.qty)

        if found:
            print(stock + " already in position for " +
                  str(qty) + " and we want " + str(alloc), end="")
            if side == 'long' and alloc < 0:
                print("... we are in wrong position so selling " +
                      str(abs(int(float(qty)))) + " and shorting " + str(abs(alloc)))
                paper_account.api.submit_order(stock, abs(
                    int(float(qty))), 'sell', "market", "day")
                paper_account2.api.submit_order(stock, abs(
                    int(float(qty))), 'sell', "market", "day")
                time.sleep(3)
                paper_account.api.submit_order(
                    stock, abs(alloc), 'sell', "market", "day")
                paper_account2.api.submit_order(
                    stock, abs(alloc), 'sell', "market", "day")

            elif side == 'short' and alloc > 0:
                print("... we are in wrong position so buying " +
                      str(abs(int(float(qty)))) + " and longing " + str(abs(alloc)))
                paper_account.api.submit_order(stock, abs(
                    int(float(qty))), 'buy', "market", "day")
                paper_account2.api.submit_order(stock, abs(
                    int(float(qty))), 'buy', "market", "day")
                time.sleep(3)
                paper_account.api.submit_order(
                    stock, abs(alloc), 'buy', "market", "day")
                paper_account2.api.submit_order(
                    stock, abs(alloc), 'buy', "market", "day")
            elif side == 'long' and alloc > 0 and alloc != qty:
                if qty < alloc:
                    print("... we are in right position but buying " +
                          str(abs(int(float(alloc - qty)))))
                    paper_account.api.submit_order(stock, abs(
                        int(float(alloc - qty))), 'buy', "market", "day")
                    paper_account2.api.submit_order(stock, abs(
                        int(float(alloc - qty))), 'buy', "market", "day")
                else:
                    print("... we are in right position but selling " +
                          str(abs(int(float(qty - alloc)))))
                    paper_account.api.submit_order(stock, abs(
                        int(float(qty - alloc))), 'sell', "market", "day")
                    paper_account2.api.submit_order(stock, abs(
                        int(float(qty - alloc))), 'sell', "market", "day")
            elif side == 'short' and alloc < 0 and alloc != qty:
                if qty > alloc:
                    print("... we are in right position but selling " +
                          str(abs(int(float(qty - alloc)))))
                    paper_account.api.submit_order(stock, abs(
                        int(float(qty - alloc))), 'sell', "market", "day")
                    paper_account2.api.submit_order(stock, abs(
                        int(float(qty - alloc))), 'sell', "market", "day")
                else:
                    print("... we are in right position but buying " +
                          str(abs(int(float(alloc - qty)))))
                    paper_account.api.submit_order(stock, abs(
                        int(float(alloc - qty))), 'buy', "market", "day")
                    paper_account2.api.submit_order(stock, abs(
                        int(float(alloc - qty))), 'buy', "market", "day")
            else:
                print("... we are good!")
        else:
            if alloc > 0:
                print(stock + " not in position buying " + str(alloc))
                paper_account.api.submit_order(
                    stock, alloc, 'buy', "market", "day")
                paper_account2.api.submit_order(
                    stock, alloc, 'buy', "market", "day")
            else:
                print(stock + " not in position selling " + str(abs(alloc)))
                paper_account.api.submit_order(
                    stock, abs(alloc), 'sell', "market", "day")
                paper_account2.api.submit_order(
                    stock, abs(alloc), 'sell', "market", "day")

    print("Stock in watchlist used " +
          str(len(sorted_allocation)) + "/" + str(len(watchlist)))
    print("Total value invested:  " + str(value))

    exit(0)
    # Other program from here ----------------------------------------------------

    print(p.get_assets_invested())

    print("----- Total Shares Owned -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have " +
              str(p.get_number_of_share_for(stock)) + " shares")

    print("----- Invested in Shares -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have invested " +
              "{:.2f}".format(p.get_capital_invested_in(stock)) + "$")

    print("----- Tot cost in Shares -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have spent " +
              "{:.2f}".format(p.get_cost_for(stock)) + "$")

    print("----- Global Total Cost  -----")
    print("Total cost: " + "{:.2f}".format(p.get_total_cost()))

    print("----- Global Total Invst -----")
    print("Total invst: " + "{:.2f}".format(p.get_total_invested()))

    print("----- Spent in Transactions -----")
    print("Transactions: " +
          "{:.2f}".format(p.get_total_cost() - p.get_total_invested()))

    main_print_loop()

''' 
This module is responsible to provide an entry point on the portfolio and 
manage the api around it
'''

import json
import time
import datetime
import api_proxy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



class Portfolio():

    def __init__(self):
        f = open("data/investments.json", "r")
        self.investments = json.load(f)
        f.close()


    def get_capital_invested_in(self, symbol):
        capital_invested = 0.0

        if symbol in self.investments:
            for investment in self.investments[symbol]["investments"]:
                capital_invested += float(investment["shares"]) * float(investment["value"])

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
                total_cost += float(investment["shares"]) * float(investment["value"]) + 1.26

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
tap = api_proxy.TradeApiProxy()
    
def main_print_loop():

    times = []
    latest_quotes = {}
    perc_diff = {}

    while True:
        now = datetime.datetime.now()
        times.append(now)
        
        for stock in p.get_assets_invested():
            close_price = tap.get_limit_minute_barset(stock, limit=2)[stock][-1].c
            if stock not in latest_quotes:
                latest_quotes[stock] = [close_price]
            else:
                latest_quotes[stock].append(close_price)

            market_value = close_price * p.get_number_of_share_for(stock)
            original_cost = p.get_cost_for(stock)
            print(stock + " marked value " + "{:.2f}".format(market_value))
            print(stock + " original cost " + "{:.2f}".format(original_cost))
            perc = (market_value - original_cost) 

            if stock not in perc_diff:
                perc_diff[stock] = [perc]
            else:
                perc_diff[stock].append(perc)

        dataframe = pd.DataFrame(None,pd.DatetimeIndex(times),None)
        for stock in p.get_assets_invested():
            dataframe[stock] = np.array(perc_diff[stock])
            dataframe[stock].plot(label=stock,figsize=(12,8),title='Return')

        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.draw()
        plt.pause(0.005)
        time.sleep(20)
        plt.clf()

    
    
    stock = 'FB'
    for i in tap.get_limit_minute_barset(stock, limit=10)[stock]:
        print(i)






if __name__ == "__main__":

    
    print(p.get_assets_invested())

    print("----- Total Shares Owned -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have " + str(p.get_number_of_share_for(stock)) + " shares")

    print("----- Invested in Shares -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have invested " + "{:.2f}".format(p.get_capital_invested_in(stock)) + "$")

    print("----- Tot cost in Shares -----")
    for stock in p.get_assets_invested():
        print("For " + stock + " you have spent " + "{:.2f}".format(p.get_cost_for(stock)) + "$")

    print("----- Global Total Cost  -----")
    print("Total cost: " + "{:.2f}".format(p.get_total_cost()))

    print("----- Global Total Invst -----")
    print("Total invst: " + "{:.2f}".format(p.get_total_invested()))

    print("----- Spent in Transactions -----")
    print("Transactions: " + "{:.2f}".format(p.get_total_cost() - p.get_total_invested()))

    main_print_loop()


''' 
This module uses the alpaca trade REST api to access and place orders
To get the real-time trading data you will need another module
that connects to a websocket streaming service
'''
import time
import math
import json
import config
import datetime
import investment
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi


class Ticker():

    def __init__(self, name: str, symbol: str, exchange: str, quote):
        self.name = name
        self.symbol = symbol
        self.exchange = exchange
        self.last_quote = quote.askprice

    def __str__(self):
        return self.name + "(" + self.symbol + ")  -  " + str(self.last_quote)


def open_connection():
    '''
    By default this will open a connection to the pater trading endpoint
    so no real money will be used for your transactions. To use a founded
    account and real money use config.ALPACA_REAL_TRADING_REST_ENDPOINT
    insead of config.ALPACA_PAPER_TRADING_REST_ENDPOINT
    '''

    # Make sure you set your API key and secret in the config module
    api = tradeapi.REST(config.ALPACA_API_KEY,
                        config.ALPACA_SECRET,
                        config.ALPACA_PAPER_TRADING_REST_ENDPOINT,
                        api_version='v2')

    return api


def check_account(api):

    # Get our account information.
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    # Check how much money we can use to open new positions.
    print('${} is available as buying power.'.format(account.buying_power))


def get_portfolio_info(api):

    # Get account info
    account = api.get_account()

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')


def get_position(api, symbol):
    # Check on our position
    try:
        position = api.get_position(symbol)
        if int(position.qty) < 0:
            print(f'Short position open for {symbol}')
    except Exception as e:
        print(str(e))


def get_positions(api):
    return api.list_positions()


def list_positions(api):
    positions = api.list_positions()

    for pos in positions:
        print("|{:>6s} ".format(pos.symbol), end="")
        #if int(pos.qty) < 0:
        #    print(f'Short position open for {symbol}')
    print("")

    for pos in positions:
        print("|{:>6s} ".format(pos.current_price), end="")
        #if int(pos.qty) < 0:
        #    print(f'Short position open for {symbol}')
    print("")


# Order structure
# - Ticker: company's symbol
# - Side: Buy, Sell
# - Type: Market, Limit (with limit you need to specify a value)
# - Quantity: count of shares

FREQUENCY_SECS = 15


def append_to_equity_file(date, tickers):

    f = open("data/stock_history.dat", "a")

    f.write(str(date))
    for t in tickers:
        f.write("," + str(t))
    f.write("\n")
    f.flush()
    f.close()


def print_header(tickers):
    f = open("data/stock_history.dat", "a")

    f.write("date")
    for t in tickers:
        f.write("," + str(t))
    f.write("\n")
    f.flush()
    f.close()


def poll_watchlist(api):

    watch_lists = api.get_watchlists()
    print(watch_lists)

    print(watch_lists[0].id)

    primary_watch_list = api.get_watchlist(watch_lists[0].id)
    print(primary_watch_list)

    local_watch_list = []

    for asset in primary_watch_list.assets:
        quote = api.get_last_quote(asset["symbol"])
        local_watch_list.append(
            Ticker(asset["name"], asset["symbol"], asset["exchange"], quote))

    tickers = ['V', 'MA', 'JNJ', 'FB']

    quotes = {}
    position_pl_perc = {}

    positions = api.list_positions()
    initial_stocks_in_positions = []
    for pos in positions:
        initial_stocks_in_positions.append(pos.symbol)

    print_header(tickers)

    while True:

        now = datetime.datetime.now()
        posi = []
        if "time" not in position_pl_perc:
            position_pl_perc['time'] = [now]
        else:
            position_pl_perc['time'].append(now)

        positions = api.list_positions()

        for symbol in initial_stocks_in_positions:
            found = False
            for pos in positions:
                if pos.symbol == symbol:
                    found = True
                    if pos.symbol in position_pl_perc:
                        position_pl_perc[pos.symbol].append(
                            float(pos.unrealized_plpc) * 100.0)
                    else:
                        position_pl_perc[pos.symbol] = [
                            float(pos.unrealized_plpc) * 100.0
                        ]
                    break
            if not found:
                if symbol in position_pl_perc:
                    position_pl_perc[symbol].append(np.nan)
                else:
                    position_pl_perc[symbol] = [np.nan]

        # quote = api.get_last_quote(quote_string)
        # print(quote)
        # ticker_values.append(quote.askprice)
        # if ticker in quotes:
        #     quotes[ticker].append(float(quote.askprice))
        # else:
        #     quotes[ticker] = [float(quote.askprice)]

        # append_to_equity_file(now, ticker_values)

        date_index = pd.DatetimeIndex(position_pl_perc['time'])
        dataframe = pd.DataFrame(None, date_index, None)
        time.sleep(FREQUENCY_SECS)
        plt.clf()
        for ticker in initial_stocks_in_positions:
            dataframe[ticker] = np.array(position_pl_perc[ticker])
            dataframe[ticker + "_ma"] = dataframe[ticker].rolling(5).mean()
            dataframe[ticker + "_ma"].plot(label=ticker,
                                           figsize=(12, 8),
                                           title='Stocks')

        plt.legend()
        plt.draw()
        plt.pause(0.005)


def main():

    api = open_connection()

    check_account(api)

    get_portfolio_info(api)

    poll_watchlist(api)

    budget = 3300.00

    # The security we'll be shorting (use can use a list here)

    watch_lists = api.get_watchlists()
    print(watch_lists)

    print(watch_lists[0].id)

    primary_watch_list = api.get_watchlist(watch_lists[0].id)
    print(primary_watch_list)

    for asset in primary_watch_list.assets:
        quote = api.get_last_quote(asset["symbol"])
        local_watch_list.append(
            Ticker(asset["name"], asset["symbol"], asset["exchange"], quote))

    for ticker in local_watch_list:
        print(str(ticker))

    per_stock_budget = budget / len(local_watch_list)

    print("Per stock budget = " + str(per_stock_budget))

    # Sort the ticker by size
    sorted_local_watch_list = []
    for ticker in local_watch_list:
        if len(sorted_local_watch_list) == 0:
            sorted_local_watch_list.append(ticker)
            continue

        inserted = False
        for i in range(0, len(sorted_local_watch_list)):
            if ticker.last_quote > sorted_local_watch_list[i].last_quote:
                sorted_local_watch_list.insert(i, ticker)
                inserted = True
                break

        if not inserted:
            sorted_local_watch_list.append(ticker)

    left_budget = budget
    bought_shares = 0
    for ticker in sorted_local_watch_list:
        per_stock_budget = left_budget / (len(sorted_local_watch_list) -
                                          bought_shares)
        shares = per_stock_budget / float(ticker.last_quote)
        rounded_down = math.floor(shares)
        print("Will buy " + str("{:5.2f}".format(shares).strip()) +
              " shares of " + ticker.symbol + " for a total of " +
              "{:5.3f}".format(ticker.last_quote * shares))
        print("Rounded is " + str(rounded_down))

        if rounded_down == 0:
            print("Will buy only one share ")
            #buy_at_market_price(api, ticker.symbol, 1)
            left_budget -= ticker.last_quote
        else:
            #buy_at_market_price(api, ticker.symbol, int(rounded_down))
            left_budget -= ticker.last_quote * rounded_down
        bought_shares += 1

    print("You are left with " + str(left_budget) + "$")
    # buy_at_market_price(api, 'TSLA', 2)
    # buy_at_market_price(api, 'MSFT', 2)
    # buy_at_market_price(api, 'F',    2)
    # buy_at_market_price(api, 'SNE',  2)
    # buy_at_market_price(api, 'NVDA', 2)
    # buy_at_market_price(api, 'ZM',   2)
    # buy_at_market_price(api, 'AMD',  2)
    # buy_at_market_price(api, 'INTC', 2)
    # buy_at_market_price(api, 'AAPL', 2)
    # buy_at_market_price(api, 'BKNG', 2)
    # buy_at_market_price(api, 'GM',   2)
    # buy_at_market_price(api, 'NFLX', 2)
    # buy_at_market_price(api, 'WORK', 2)
    # buy_at_market_price(api, 'CSCO', 2)
    # buy_at_market_price(api, 'TWTR', 2)
    # buy_at_market_price(api, 'IBM',  2)
    # buy_at_market_price(api, 'PYPL', 2)
    # buy_at_market_price(api, 'EXPE', 2)
    # buy_at_market_price(api, 'BABA', 2)

    print("Listing open positions: ", end="")
    number_of_positions = len(get_positions(api))
    if number_of_positions > 0:
        print("There are " + str(number_of_positions) + " positions open")
        list_positions(api)
        for symbol in investment.get_portfolio_stocks():
            #shares = investment.get_shares_for(symbol)
            #order = api.submit_order(symbol, shares, 'buy', 'market', 'day')
            # print("Market order submitted for: " + symbol)

            # # Submit a limit order to attempt to grow our short position
            # # First, get an up-to-date price for our symbol
            # symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
            # symbol_price = symbol_bars[symbol]['close']
            # # Submit an order for one share at that price
            # order = api.submit_order(symbol, 1, 'sell', 'limit', 'day', symbol_price)
            # print("Limit order submitted.")

            # # Wait a second for our orders to fill...
            # print('Waiting...')
            # time.sleep(1)

            get_position(api, symbol)
    else:
        print("There are no positions open")
    # Submit a market order to open a short position of one share


if __name__ == '__main__':
    main()

import time
import datetime
import traceback
import numpy as np
import pandas as pd
import conf.secret as config
import matplotlib.pyplot as plt
import alpaca_trade_api as tradeapi

POLLING_TIME_SECS = 10
LOOSE_THRESHOLD = 0.5

INITIAL_TARGET_GAIN = 1.0
INITIAL_TARGET_LOSS = -0.5
GAP_ON_WIN = 1.5

PER_TRADE_BUDGET = 900.0

WIN_THRESHOLD = 1
watchlist = [
    "TWTR", "SNE", "PYPL", "NVDA", "MA", "INTC", "FB", "EBAY", "BA", "AAPL",
    "BYND", "V", "AMD", "AXP", "CSCO", "EBAY", "EA", "EXPE", "IBM", "NVTA",
    "MSFT", "NFLX", "PTON", "RCL", "WORK", "ZM", "KO", "PFE", "DIS", "BABA",
    "MCD", "SBUX", "JPM", "ADBE", "JNJ"
]

# Problematic because the low value
# "F","IMGN", "NBL","MPC",

# Can't short

targets = dict()


def init_all_stock_targets(api):
    global targets

    for stock in watchlist:
        quote = api.get_last_quote(stock)
        init_target(stock)
        adjust_stop_target(stock,
                           float(quote.askprice) - float(quote.bidprice))


def init_target(stock):
    global targets

    targets[stock] = {
        "gain": INITIAL_TARGET_GAIN,
        "loss": INITIAL_TARGET_LOSS,
        "gap_per_share": 0.0,
        "scaled": False
    }


def adjust_stop_target(stock, value):

    print("Adjusting stop loss for " + stock + " to " + str(value))
    targets[stock]["gap_per_share"] = value


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

    balance_change = float(account.equity) - float(account.last_equity)
    # Check how much money we can use to open new positions.
    print("\r", end="", flush=True)
    print('Equity is ${} balance change: ${:.2f}'.format(
        account.equity, balance_change),
          end="",
          flush=True)

    return account.equity


def create_baseline():

    initial_values = {}

    return initial_values


def list_orders(api):

    orders = api.list_orders(status='all')

    for order in orders:
        if order.status == 'filled':
            print(order.symbol + " " + order.filled_avg_price)


def list_positions(api):
    positions = api.list_positions()

    for pos in positions:
        print("|{:>6s} ".format(pos.symbol), end="")
    print("")

    for pos in positions:
        print("|{:>6s} ".format(pos.current_price), end="")
    print("")


def list_assets(api):

    assets = api.list_assets()
    for asset in assets:
        print(asset)
    print("There are " + str(len(assets)) + " available")


def value_close_to_threshold(value):

    print("-------------------")
    print("value " + str(value))
    rem = round(PER_TRADE_BUDGET / value)
    print("rem " + str(rem))

    if rem * value > (PER_TRADE_BUDGET * 1.1):
        print("Stock number is " + str(rem))
        return rem - 1

    print("Stock number is " + str(rem))
    return rem


def get_cost_basis(api):

    positions = api.list_positions()

    cost_basis = {}
    for pos in positions:
        cost_basis[pos.symbol] = float(pos.cost_basis)

    return cost_basis


def append_to_market_value(api, gain):

    positions = api.list_positions()

    for pos in positions:
        if pos.symbol in gain:
            gain[pos.symbol].append(
                float(pos.market_value) - float(pos.cost_basis))
        else:
            gain[pos.symbol] = [
                float(pos.market_value) - float(pos.cost_basis)
            ]

    return positions


def update_positions(api, gain):

    positions = api.list_positions()

    for pos in positions:
        gain[pos.symbol] = (float(pos.market_value) - float(pos.cost_basis))

    return positions


def analyse_gain(gain):

    loosers = []
    winners = []
    for stock in gain:
        if gain[stock] < targets[stock]["loss"]:
            if targets[stock]["loss"] <= INITIAL_TARGET_LOSS:
                print(stock + " is losing " + str(gain[stock]))
            else:
                print(stock + " exausted the positive trend " +
                      str(targets[stock]["loss"]))
            loosers.append(stock)
        if gain[stock] > targets[stock]["gain"]:
            print(stock + " is winning " + str(gain[stock]))
            winners.append(stock)

    return winners, loosers


def submit_order(api, stock, quantity, side):

    qty = abs(int(float(quantity)))
    if qty > 0:
        print("Submitting order for " + str(quantity) + " shares of " + stock)
        try:
            api.submit_order(stock, abs(int(float(qty))), side, "market",
                             "day")
            print("Following order | COMPLETED | " + str(qty) + " " + stock +
                  " " + side + " | ")
        except Exception as e:
            print("Following order |  FAILURE  | " + str(qty) + " " + stock +
                  " " + side + " | ")
            print(e)
            traceback.print_exc()
    time.sleep(0.5)


def scale_targets(stock):
    global targets

    targets[stock]["gain"] += 1.0

    if targets[stock]["loss"] <= INITIAL_TARGET_LOSS:
        targets[stock]["loss"] = targets[stock]["gain"] - GAP_ON_WIN + (
            targets[stock]["gain"] / 5)
    else:
        targets[stock]["loss"] += 1.0

    targets[stock]["scaled"] = True

    print(stock + " hit the target scaling to gain = " +
          str(targets[stock]["gain"]) + "$, loss = " +
          str(targets[stock]["loss"]) + "$")


def reset_gain(stock):
    pass


# def rebalance_targets():


def trade_targets(api, winners, loosers, positions):

    # Rebet on winners
    if len(winners) > 0:
        for stock in winners:
            for pos in positions:
                if stock == pos.symbol:
                    scale_targets(stock)
                    # if pos.side == "long":
                    #     submit_order(api, pos.symbol, pos.qty, "sell")
                    # else:
                    #     submit_order(api, pos.symbol, pos.qty, "buy")

    # Change side on loosers
    if len(loosers) > 0:
        for stock in loosers:
            for pos in positions:
                if stock == pos.symbol:
                    # This will invert the direction of the trade
                    if targets[stock]["scaled"] is False:
                        if pos.side == "long":
                            submit_order(api, pos.symbol, pos.qty, "sell")
                            submit_order(api, pos.symbol, pos.qty, "sell")
                        else:
                            submit_order(api, pos.symbol, pos.qty, "buy")
                            submit_order(api, pos.symbol, pos.qty, "buy")
                    else:
                        if pos.side == "long":
                            submit_order(api, pos.symbol, pos.qty, "sell")
                            submit_order(api, pos.symbol, pos.qty, "buy")
                        else:
                            submit_order(api, pos.symbol, pos.qty, "buy")
                            submit_order(api, pos.symbol, pos.qty, "sell")
                    init_target(stock)


def main_loop(api):
    equity = check_account(api)
    now = datetime.datetime.now()

    time_array = []
    stock_array = []

    time_array.append(now)
    stock_array.append(float(equity))

    date_index = pd.DatetimeIndex(time_array)
    dataframe = pd.DataFrame(None, date_index, None)
    dataframe["Equity"] = np.array(stock_array)

    while True:

        time.sleep(30)
        plt.clf()

        equity = check_account(api)
        now = datetime.datetime.now()

        stock_array.append(float(equity))
        time_array.append(now)

        date_index = pd.DatetimeIndex(np.array(time_array))
        dataframe = pd.DataFrame(None, date_index, None)
        dataframe["Equity"] = np.array(stock_array)
        dataframe["Equity"].plot(label="equity",
                                 figsize=(12, 8),
                                 title='Equity value')
        plt.legend()
        plt.draw()
        plt.pause(0.005)


def trade_watchlist(api):

    positions = api.list_positions()

    print("POSITIONS ----------------------------------")
    for pos in positions:
        print(pos)

    # Positioning for the stocks that we have in the watchlist that we are missing
    for stock in watchlist:

        found = False
        for pos in positions:
            if pos.symbol == stock:
                found = True
                break

        if found is False:
            quote = api.get_last_quote(stock)
            quote_value = quote.bidprice
            print("Got a quote for " + stock +
                  " not in position so trading it")
            submit_order(api, stock, value_close_to_threshold(quote_value),
                         'buy')
        else:
            print("Position already open for " + stock)


def awaitMarketOpen(api):
    isOpen = api.get_clock().is_open
    while (not isOpen):
        clock = api.get_clock()
        openingTime = clock.next_open.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(
            tzinfo=datetime.timezone.utc).timestamp()
        timeToOpen = int((openingTime - currTime) / 60)
        print(str(timeToOpen) + " minutes til market open.")
        time.sleep(60)
        isOpen = api.get_clock().is_open


def main():

    api = open_connection()
    list_positions(api)
    init_all_stock_targets(api)

    awaitMarketOpen(api)
    trade_watchlist(api)

    gain = {}
    update_positions(api, gain)

    print("You are trading on " + str(len(watchlist)) + " assets")
    # time_array.append(datetime.datetime.now())
    # date_index = pd.DatetimeIndex(np.array(time_array))
    # dataframe = pd.DataFrame(None, date_index, None)
    # idx = {}
    # fig_printed = False
    # legend = True
    while True:

        awaitMarketOpen(api)
        # trade_watchlist(api)
        # plt.clf()
        # time_array.append(datetime.datetime.now())
        positions = update_positions(api, gain)
        # date_index = pd.DatetimeIndex(np.array(time_array))
        # dataframe = pd.DataFrame(None, date_index, None)

        for pos in positions:
            # print(pos.symbol + " " + pos.side + " " + pos.qty)
            if pos.symbol not in gain:
                del gain[pos.symbol]
            # dataframe[stock] = np.array(gain[stock])
            # if not fig_printed:
            # dataframe[stock].plot(label=stock, figsize=(12, 8), title='Gain per stock')

        win, lose = analyse_gain(gain)
        trade_targets(api, win, lose, positions)

        # plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        # plt.draw()
        # plt.pause(0.005)
        time.sleep(POLLING_TIME_SECS)


if __name__ == '__main__':
    main()

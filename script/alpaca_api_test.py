import time
from lib.trading.alpaca import AlpacaTrading
from data.watchlist import universe


def populate_watchlist(account):
    for elem in universe:
        account.add_symbol_to_watchlist(elem)


if __name__ == "__main__":

    paper_api = TradeApiProxy('paper')
    paper_api2 = TradeApiProxy('paper2')
    live_api = TradeApiProxy('live')

    # populate_watchlist(paper_api)
    # populate_watchlist(paper_api2)
    # populate_watchlist(live_api)

    # live_api.sort_watchlist()
    # paper_api.sort_watchlist()
    # paper_api2.sort_watchlist()

    #print("Paper trading has " + str(len(paper_api.get_watchlist())))
    #print("Paper2 trading has " + str(len(paper_api2.get_watchlist())))
    #print("Live trading has " + str(len(live_api.get_watchlist())))

    # print("Listing all orders ----------------------")
    # all_orders = paper_api.list_all_orders()
    # for order in all_orders:
    #     print(order.symbol + " " + order.status)

    # print("Listing open orders ----------------------")
    # for order in paper_api.list_open_orders():
    #     print(order.symbol + " " + order.status)

    # print("Listing closed orders ----------------------")
    # for order in paper_api.list_closed_orders():
    #     print(order.symbol + " " + order.status)

    # Create a TM limit buy order from 1 share at a price of 33.10 if not already there
    # for order in paper_api.list_open_orders():
    #     if order.symbol == 'TM' and \
    #        order.qty == '1' and \
    #        order.side == 'buy' and \
    #        order.type == 'limit':
    #        break
    # else:
    #     paper_api.api.submit_order(
    #         symbol = 'TM',
    #         qty = 1,
    #         side = 'buy',
    #         type = 'limit',
    #         time_in_force = 'gtc',
    #         limit_price = '33.10'
    #     )

    # paper_api.api.cancel_all_orders()

    # time.sleep(5)

    # print("Let's try to replace one order ----------------------")
    # all_orders = paper_api.list_all_orders()
    # for order in all_orders:
    #     if order.status == 'new' and order.type != 'market':
    #         print("Replacing order: " + str(order))

    #         limit = stop = None
    #         if order.limit_price != None:
    #             limit = "{:.2f}".format(float(order.limit_price) * 1.1)
    #         if order.stop_price != None:
    #             stop = "{:.2f}".format(float(order.stop_price) * 1.1)
    #         tif = order.time_in_force

    #         paper_api.replace_order(
    #             id = order.id,
    #             qty = order.qty,
    #             limit = limit,
    #             stop = stop)
    #         break

    stock_peaks = dict()
    global open_orders
    open_oders = paper_api.list_open_orders(use_cache=False)
    api = live_api
    while True:
        print("Getting positions...")
        positions = paper_api.get_positions()
        for pos in positions:
            market_value = pos.market_value
            if pos.symbol in stock_peaks:
                if pos.side == 'long':
                    stock_peaks[pos.symbol] = max(
                        stock_peaks[pos.symbol], market_value)
                else:
                    stock_peaks[pos.symbol] = min(
                        stock_peaks[pos.symbol], market_value)

                if stock_peaks[pos.symbol] == market_value:
                    print("Updating order for " + pos.symbol)
                    try:
                        api.update_stop_loss_order_for(pos)
                    except Exception as e:
                        print(e)
            else:
                stock_peaks[pos.symbol] = market_value
                print("Placing stop loss order for " + pos.symbol)

                api.cover_position_with_stop_loss(pos)

        time.sleep(15)
    # print("Listing new orders ----------------------")
    # for order in paper_api.list_new_orders():
    #     print(order.symbol + " " + order.status)

    # print("Listing closed orders ----------------------")
    # for order in paper_api.list_closed_orders():
    #     print(order.symbol + " " + order.status)

import time
from api_proxy import TradeApiProxy


if __name__ == "__main__":

    paper_api = TradeApiProxy('paper')

    # paper_api.sort_watchlist()

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
    while True:
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
                        paper_api.update_stop_loss_order_for(pos)
                    except Exception as e:
                        print(e)
            else:
                stock_peaks[pos.symbol] = market_value
                print("Placing stop loss order for " + pos.symbol)

                paper_api.cover_position_with_stop_loss(pos)

        time.sleep(15)
    # print("Listing new orders ----------------------")
    # for order in paper_api.list_new_orders():
    #     print(order.symbol + " " + order.status)

    # print("Listing closed orders ----------------------")
    # for order in paper_api.list_closed_orders():
    #     print(order.symbol + " " + order.status)

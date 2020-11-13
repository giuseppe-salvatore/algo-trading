from datetime import datetime
from lib.util.logger import log
from lib.trading.generic import TradeSession, Trade, Order


class TradingPlatform():

    @staticmethod
    def get_trading_platform(platform_name):
        if platform_name == "simulation":
            return SimulationPlatform()
        else:
            raise ValueError("Unknown trading platform: {}".format(platform_name))

class SimulationPlatform(TradingPlatform):

    def __init__(self):
        self.active_orders = dict()
        self.executed_orders = dict()
        self.cancelled_orders = dict()
        self.rejected_orders = dict()
        self.trading_session = TradeSession()

    def estimate_current_price_for(self, symbol):
        log.warning("Just a placeholder for now, update with actual logic")
        return 10.0

    def get_order(self, id):
        if id in self.active_orders:
            return self.active_orders[id]

        if id in self.executed_orders:
            return self.executed_orders[id]

        if id in self.cancelled_orders:
            return self.cancelled_orders[id]

        if id in self.rejected_orders:
            return self.rejected_orders[id]

        return None

    def submit_order(self,
                     symbol: str,
                     quantity: int,
                     side: str,
                     date: datetime,
                     flavor: str = "market",
                     limit_price: float = None,
                     stop_price: float = None,
                     take_profit_price: float = None,
                     stop_loss_price: float = None):
        order = Order(symbol,
                      quantity,
                      side,
                      date,
                      flavor,
                      limit_price,
                      stop_price,
                      take_profit_price,
                      stop_loss_price)
        # TODO we need some sort of rules in place to check if we need to reject the order

        log.debug("Activating {} order\n{}".format(order.flavor, order))
        self.active_orders[order.id] = order

        # We might need to put the leg orders into active status even if there will
        # be transitioning pretty soon in executed status
        take_profit_order: Order = order.get_take_profit_order()
        if take_profit_order is not None:
            self.active_orders[take_profit_order.id] = take_profit_order

        stop_loss_order: Order = order.get_stop_loss_order()
        if stop_loss_order is not None:
            self.active_orders[stop_loss_order.id] = stop_loss_order

        if order.flavor == 'market':
            log.debug("Executing market order right away {}".format(order.id))
            self._execute_order(order.id)

        return order.id

    def print_all_orders(self):

        print("Active Orders ---------------------")
        for element in self.active_orders:
            print(element)
            print(self.active_orders[element])

        print("Executed Orders ---------------------")
        for element in self.executed_orders:
            print(element)
            print(self.executed_orders[element])

        print("Cancelled Orders ---------------------")
        for element in self.cancelled_orders:
            print(element)
            print(self.cancelled_orders[element])

    def _execute_order(self, order_id):
        if order_id not in self.active_orders:
            raise ValueError("Cannot execute orders not in active order lists")
        order: Order = self.active_orders[order_id]
        log.debug("Executing order\n{}".format(order))

        results = order.execute(self.estimate_current_price_for(order.symbol), order.date)
        trade: Trade = results[0]
        limit_order: Order = results[1]
        stop_order: Order = results[2]
        # TODO here we could have the leg orders to activate if it's a braket order
        del self.active_orders[order.id]
        self.executed_orders[order.id] = order
        self.trading_session.add_trade(trade)

        # In case there was a take_profit converted to a limit order then we
        # need to move it in the correspondent status
        if limit_order is not None:
            self.active_orders[limit_order.id] = limit_order
            take_profit_order = order.get_take_profit_order()
            del self.active_orders[take_profit_order.id]
            self.executed_orders[take_profit_order.id] = take_profit_order

        if stop_order is not None:
            self.active_orders[stop_order.id] = stop_order
            stop_loss_order = order.get_stop_loss_order()
            del self.active_orders[stop_loss_order.id]
            self.executed_orders[stop_loss_order.id] = stop_loss_order

        # # Executing leg orders if present
        # leg_order = order.get_take_profit_order()
        # if leg_order is not None:
        #     self._execute_order(leg_order)

        # leg_order = order.get_stop_loss_order()
        # if leg_order is not None:
        #     self._execute_order(leg_order)

    def cancel_order(self, order_id):
        if order_id not in self.active_orders:
            raise ValueError("Order {} is not active".format(order_id))

        order: Order = self.active_orders[order_id]
        log.debug("Cancelling {} order\n{}".format(order.flavor, order))
        del self.active_orders[order_id]
        self.cancelled_orders[order_id] = order
        order.status = 'cancelled'

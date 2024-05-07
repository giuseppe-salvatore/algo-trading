from datetime import datetime
from lib.util.logger import log
from lib.trading.generic import TradeSession, Trade, Order, Candle, Position


class TradingPlatform():

    @staticmethod
    def get_trading_platform(platform_name):
        if platform_name == "simulation":
            return SimulationPlatform()
        else:
            raise ValueError(
                "Unknown trading platform: {}".format(platform_name))


class SimulationPlatform(TradingPlatform):

    def __init__(self):
        self.active_orders = dict()
        self.executed_orders = dict()
        self.cancelled_orders = dict()
        self.rejected_orders = dict()
        self.trading_session = TradeSession()
        self.current_candle = dict()

    def clear(self):
        self.active_orders = dict()
        self.executed_orders = dict()
        self.cancelled_orders = dict()
        self.rejected_orders = dict()
        self.trading_session = TradeSession()
        self.current_candle = dict()

    def get_current_price_for(self, symbol):
        current_price = self.current_candle[symbol].close
        log.debug("Current price used: " + str(current_price))
        return current_price

    def get_current_time_for(self, symbol):
        current_time = self.current_candle[symbol].date_time
        return current_time

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

    def tick(self, symbol: str, candle: Candle):
        # log.debug(" Platform Tick - {} {:.2f} (H:{:.2f},L:{:.2f}) ".format(
        #     candle.date_time,
        #     candle.close,
        #     candle.high,
        #     candle.low
        # ))
        self.current_candle[symbol] = candle
        return self._check_active_orders(symbol)

    def _check_limit_order(self, lo: Order):
        low = self.current_candle[lo.symbol].low
        if lo.side == 'buy' and lo.limit_price >= low:
            log.debug(
                "Triggering limit buy order low price {:.2f} <= current price {:.2f}"
                .format(
                    low,
                    lo.limit_price,
                ))
            self._execute_order(lo.id)
            return True

        high = self.current_candle[lo.symbol].high
        if lo.side == 'sell' and lo.limit_price <= high:
            log.debug(
                "Triggering limit sell order high price {:.2f} >= sell limit {:.2f}"
                .format(
                    high,
                    lo.limit_price,
                ))
            self._execute_order(lo.id)
            return True

        return False

    def _check_stop_order(self, lo: Order):
        high = self.current_candle[lo.symbol].high
        if lo.side == 'buy' and lo.stop_price <= self.current_candle[
                lo.symbol].high:
            log.debug(
                "Triggering stop buy order high price {:.2f} >= current price {:.2f}"
                .format(high, lo.stop_price))
            self._execute_order(lo.id)
            return True

        low = self.current_candle[lo.symbol].low
        if lo.side == 'sell' and lo.stop_price >= self.current_candle[
                lo.symbol].low:
            log.debug(
                "Triggering stop sell order low price {:.2f} <= current price {:.2f}"
                .format(low, lo.stop_price))
            self._execute_order(lo.id)
            return True

        return False

    def _check_active_orders(self, symbol):

        orders_executed = 0
        for order_id in list(self.active_orders):
            if order_id in self.active_orders:
                o: Order = self.active_orders[order_id]
                if o.symbol == symbol:
                    if o.flavor == 'limit':
                        if self._check_limit_order(o):
                            orders_executed += 1
                    elif o.flavor == 'stop':
                        if self._check_stop_order(o):
                            orders_executed += 1
        return True if orders_executed > 0 else False

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
        order = Order(symbol, quantity, side, date, flavor, limit_price,
                      stop_price, take_profit_price, stop_loss_price)

        close_price = self.current_candle[symbol].close
        if order.side == 'buy':
            # TODO we need proper limits here
            if take_profit_price is not None and take_profit_price <= close_price:
                raise ValueError(
                    "{} {} {} order's take profit price {:.2f} below current close price {:.2f}"
                    .format(order.symbol, order.flavor, 'buy',
                            take_profit_price, close_price))
            # TODO we need proper limits here
            if stop_loss_price is not None and stop_loss_price >= close_price:
                raise ValueError(
                    "{} {} {} order's stop_loss price {:.2f} above current close price {:.2f}"
                    .format(order.symbol, order.flavor, 'sell',
                            stop_loss_price, close_price))
        if order.side == 'sell':
            # TODO we need proper limits here
            if take_profit_price is not None and take_profit_price >= close_price:
                raise ValueError(
                    "{} {} {} order's take profit price {:.2f} above current close price {:.2f}"
                    .format(order.symbol, order.flavor, 'sell',
                            take_profit_price, close_price))
            # TODO we need proper limits here
            if stop_loss_price is not None and stop_loss_price <= close_price:
                raise ValueError(
                    "{} {} {} order's stop_loss price {:.2f} below current close price {:.2f}"
                    .format(order.symbol, order.flavor, 'buy', stop_loss_price,
                            close_price))

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
            # TODO self.trading_session.get_orders(symbols)

        if order.flavor == 'market':
            log.debug(
                "Executing market {} {} ({}) order right away filled at {:.2f}"
                .format(order.side, order.symbol, order.id[:6],
                        self.current_candle[symbol].close))
            self._execute_order(order.id)

        return order.id

    def print_all_orders(self):  # pragma: no cover

        log.debug("Active Orders ---------------------")
        for element in self.active_orders:
            log.debug(self.active_orders[element])

        log.debug("Executed Orders ---------------------")
        for element in self.executed_orders:
            log.debug(self.executed_orders[element])

        log.debug("Cancelled Orders ---------------------")
        for element in self.cancelled_orders:
            log.debug(self.cancelled_orders[element])

    def _execute_order(self, order_id):
        if order_id not in self.active_orders:
            raise ValueError(
                "Cannot execute order not in active order list {}".format(
                    order_id))
        order: Order = self.active_orders[order_id]
        log.debug("Executing {} {} {} order".format(order.symbol, order.flavor,
                                                    order.side))

        # leg orders don't generate a trade when executed, they are only converted
        trade: Trade = order.execute(self.get_current_price_for(order.symbol),
                                     self.get_current_time_for(order.symbol))
        leg_order_type = ['take_profit', 'stop_loss']
        if order.flavor not in leg_order_type:
            if trade is None:
                raise ValueError(
                    "Execution of {} {} {} order should have generated a trade"
                    .format(order.symbol, order.flavor, order.side))
            del self.active_orders[order.id]
            self.executed_orders[order.id] = order
            self.trading_session.add_trade(trade)
            position: Position = self.trading_session.get_current_position(
                trade.symbol)
            if position is not None:
                if 'take_profit' in order._legs_by_type:
                    tp = order._legs_by_type['take_profit']
                    position.set_take_profit(tp)
                if 'stop_loss' in order._legs_by_type:
                    sl = order._legs_by_type['stop_loss']
                    position.set_stop_loss(sl)

            # We need to cancel all the linked orders, i.e. both legs of a bracket order must be
            # finalised
            for linked in order._linked_with:
                self.cancel_order(linked.id, trade.date)

    def cancel_order(self, order_id: str, date=datetime.now()):
        order: Order = self.get_order(order_id)
        if order is None:
            raise ValueError("Cannot find order {}".format(order_id))
        if order_id not in self.active_orders:
            raise ValueError(
                "Expected {} {} {} order to be active ({})".format(
                    order.symbol, order.flavor, order.side, order.side))

        log.debug("Cancelling {} order\n{}".format(order.flavor, order))
        del self.active_orders[order_id]
        self.cancelled_orders[order_id] = order
        order.cancel(date)

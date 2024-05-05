import random
import datetime
from lib.util.logger import log

capital_invested = 0.0
max_capital_invested = 0.0


def get_max_capital_invested():
    global max_capital_invested
    return max_capital_invested


class Trade:
    def __init__(
        self, symbol: str, quantity: int, price: float, side: str, date: datetime
    ):
        self._date = date
        self._side = side
        self._date = date
        self._price = price
        self._symbol = symbol
        self._quantity = quantity

    @property
    def price(self):
        return self._price

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, val):
        self._date = val

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, val):
        self._side = val

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, val):
        self._symbol = val

    @price.setter
    def price(self, val):
        self._price = val

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, val):
        self._quantity = val

    def __str__(self):
        str_repr = ""
        if self.side == "buy":
            str_repr += "Bought "
        else:
            str_repr += "Sold "
        str_repr += (
            str(self.quantity) +
            " shares at " +
            str(self.price) +
            "$ on " +
            str(self.date)
        )
        return str_repr


class Position:
    def __init__(self, symbol: str, trade: Trade):
        self.side = "long" if trade.side == "buy" else "short"
        self.open_time = trade.date
        self.close_time = None
        self.symbol = symbol

        self.trades = [trade]
        self.leg_orders = {"take_profit": None, "stop_loss": None}

        # Batches will collect the current status whilst orders the
        # whole history
        self.batches = (
            [{"quantity": trade.quantity, "price": trade.price}]
            if trade.side == "buy"
            else [{"quantity": -trade.quantity, "price": -trade.price}]
        )

        log.debug(
            "Opening {} {} position ({})".format(self.symbol, self.side, trade.quantity)
        )

        global capital_invested
        global max_capital_invested
        capital_invested -= abs(trade.quantity * trade.price)
        max_capital_invested = min(capital_invested, max_capital_invested)
        log.debug("Trade executed: {}".format(trade))

    def get_open_price(self):
        return self.trades[0].price

    def get_close_price(self):
        if self.is_open():
            return None
        return self.trades[-1].price

    def get_open_datetime(self):
        return self.trades[0].date

    def get_close_datetime(self):
        if self.is_open():
            return None
        return self.trades[-1].date

    def get_total_shares(self):
        total_shares = 0
        for batch in self.batches:
            total_shares += batch["quantity"]
        return total_shares

    def get_average_price(self):
        total_price = 0.0
        for batch in self.batches:
            total_price += batch["price"] * batch["quantity"]
        return total_price / self.get_total_shares()

    def get_profit(self):
        pl = 0.0
        for t in self.trades:
            pl += (
                -(t.price * t.quantity) if t.side == "buy" else +(t.price * t.quantity)
            )
        return pl

    def get_current_profit(self, curr_price):
        if self.is_open():
            avg_price = self.get_average_entry_price()
            profit = (curr_price - avg_price) * self.get_total_shares()
            return profit
        return 0.0

    def update_position(self, trade: Trade):
        if trade.symbol != self.symbol:
            msg = "Updating position for " + trade.symbol
            msg += " but position is open for " + self.symbol
            log.error(msg)
            raise ValueError(msg)

        if not self.is_open():
            log.error("Trying to update a closed position")
            raise ValueError("Trying to update a closed position")

        log.debug("Trade executed: {}".format(trade))

        if trade.side == "buy":
            if self.side == "long":
                self.batches.append({"quantity": trade.quantity, "price": trade.price})
            else:
                self._remove_shares(trade)
        elif trade.side == "sell":
            if self.side == "short":
                self.batches.append(
                    {"quantity": -trade.quantity, "price": -trade.price}
                )
            else:
                self._remove_shares(trade)
        else:
            log.error("Unexpected trade side: " + trade.side)
            raise ValueError("Unexpected trade side: " + trade.side)

        self.trades.append(trade)

        global capital_invested
        if self.get_total_shares() == 0:
            log.debug(
                "Closing {} {} position (profit = {:.2f})".format(
                    self.symbol, self.side, self.get_profit()
                )
            )
            capital_invested += abs(trade.quantity * trade.price)

    def _remove_shares(self, trade: Trade):
        tradable_shares = self.get_total_shares()
        trade_quantity = trade.quantity if trade.side == "buy" else -trade.quantity
        if abs(tradable_shares) >= abs(trade_quantity):
            left_to_trade = trade_quantity
            for batch in self.batches:
                if abs(batch["quantity"]) > abs(left_to_trade):
                    batch["quantity"] += left_to_trade
                    left_to_trade = 0
                    break
                elif abs(batch["quantity"]) == abs(left_to_trade):
                    batch["quantity"] += left_to_trade
                    left_to_trade = 0
                    break
                elif abs(batch["quantity"]) < abs(left_to_trade):
                    left_to_trade += batch["quantity"]
                    batch["quantity"] = 0
            self.batches = [batch for batch in self.batches if batch["quantity"] != 0]
        else:
            log.error(
                "Invalid trade cannot {} more than {}, {} not acceptable".format(
                    trade.side, tradable_shares, trade_quantity
                )
            )
            raise ValueError(
                "Invalid trade cannot " +
                trade.side +
                " more than " +
                str(tradable_shares)
            )

    def has_leg_orders(self):
        if self.leg_orders["take_profit"] is not None:
            return True
        else:
            if self.leg_orders["stop_loss"] is not None:
                return True

    def get_leg_orders(self):
        return self.leg_orders

    def get_leg(self, order_type: str):
        return self.leg_orders[order_type]

    def set_take_profit(self, order):
        self.leg_orders["take_profit"] = order

    def set_stop_loss(self, order):
        self.leg_orders["stop_loss"] = order

    def get_average_entry_price(self):
        average_price = 0.0
        for batch in self.batches:
            average_price += batch["quantity"] * batch["price"]
        return average_price / abs(self.get_total_shares())

    def is_open(self):
        return False if len(self.batches) == 0 else True

    def get_trades(self):
        return self.trades

    def __str__(self):
        str_rep = ""
        str_rep += "Position{\n"
        str_rep += " symbol  = {}\n".format(self.symbol)
        str_rep += " is_open = {}\n".format(self.is_open())
        str_rep += " profit  = {:.2f}$\n".format(self.get_profit())
        str_rep += "}\n"
        return str_rep

    def liquidate(self, price: float, date: datetime):
        if self.is_open():
            side = "sell" if self.side == "long" else "buy"
            previous_trade_date: datetime = self.trades[-1].date
            close_date = datetime.datetime(
                previous_trade_date.year,
                previous_trade_date.month,
                previous_trade_date.day,
                date.hour,
                date.minute,
            )
            self.update_position(
                Trade(
                    self.symbol, abs(self.get_total_shares()), price, side, close_date
                )
            )
            log.debug(
                "{}' position liquidated, profit = {:.2f}$".format(
                    self.symbol, self.get_profit()
                )
            )


class Candle:
    def __init__(self, idx, data):
        self.date_time = idx
        self.open = data["open"]
        self.close = data["close"]
        self.high = data["high"]
        self.low = data["low"]
        self.volume = data["volume"]


class TradeSession:
    def __init__(self):
        self.positions = dict()
        self.orders = dict()

    def get_symbols(self):
        return self.positions.keys()

    def add_trade(self, trade: Trade):
        if trade.symbol not in self.positions:
            self.positions[trade.symbol] = [Position(trade.symbol, trade)]
        else:
            latest_position: Position = self.positions[trade.symbol][-1]
            if latest_position.is_open():
                latest_position.update_position(trade)
            else:
                self.positions[trade.symbol].append(Position(trade.symbol, trade))

    def get_orders(self, symbol):
        if symbol in self.orders:
            return self.orders[symbol]
        else:
            return None

    def get_total_profit(self):
        total_profit = 0.0
        for symbol in self.positions.keys():
            total_profit += self.get_profit_for_symbol(symbol)
        return total_profit

    def get_profit_for_symbol(self, symbol: str):
        profit = 0.0
        if symbol not in self.positions:
            return profit

        for position in self.positions[symbol]:
            profit += position.get_profit()
        return profit

    def liquidate(self, symbol: str, price: float, date: datetime):
        pos = self.get_current_position(symbol)
        if pos is not None:
            pos.liquidate(price, date)

        # if (symbol in pos and len(pos[symbol]) > 0 and pos[symbol][-1].is_open()):
        #     pos[symbol][-1].liquidate(price, date)

    def get_positions(self, symbol: str):
        return self.positions[symbol]

    def get_positions_between_dates(self, symbol: str, start_date, end_date):
        positions = []
        for position in self.positions[symbol]:
            open_datetime = position.get_open_datetime()
            if open_datetime > start_date and open_datetime < end_date:
                positions.append(position)
        return positions

    def get_current_position(self, symbol: str):
        if symbol in self.positions and len(self.positions[symbol]):
            if self.positions[symbol][-1].is_open():
                return self.positions[symbol][-1]
        return None

    def get_total_success_rate(self):
        won = 0
        lost = 0
        for symbol in self.positions.keys():
            for pos in self.positions[symbol]:
                if pos.get_profit() > 0:
                    won += 1
                else:
                    lost += 1
        return float(won) / float(won + lost)

    def get_total_trades(self):
        trades = 0
        for symbol in self.positions.keys():
            trades += len(self.positions[symbol])
        return trades

    def get_won_trades(self):
        won = 0
        for symbol in self.positions.keys():
            for pos in self.positions[symbol]:
                if pos.get_profit() > 0:
                    won += 1
        return won

    def get_max_session_profit_for_symbol(self, symbol):
        curr_profit = 0.0
        max_profit = -float("inf")
        # for pos in self.positions[symbol]:
        #     print("Profit {:.2f}".format(pos.get_profit()))
        for pos in self.positions[symbol]:
            curr_profit += pos.get_profit()
            max_profit = max(max_profit, curr_profit)
        return max_profit

    def get_min_session_profit_for_symbol(self, symbol):
        curr_profit = 0.0
        min_profit = +float("inf")
        for pos in self.positions[symbol]:
            curr_profit += pos.get_profit()
            min_profit = min(min_profit, curr_profit)
        return min_profit

    def get_max_position_profit_for_symbol(self, symbol):
        max_profit = -float("inf")
        for pos in self.positions[symbol]:
            curr_profit = pos.get_profit()
            max_profit = max(max_profit, curr_profit)
        return max_profit

    def get_min_position_profit_for_symbol(self, symbol):
        min_profit = +float("inf")
        for pos in self.positions[symbol]:
            curr_profit = pos.get_profit()
            min_profit = min(min_profit, curr_profit)
        return min_profit


class Order:
    def __init__(
        self,
        symbol: str,
        quantity: int,
        side: str,
        date: datetime,
        flavor: str = "market",
        limit_price: float = None,
        stop_price: float = None,
        take_profit_price: float = None,
        stop_loss_price: float = None,
    ):
        # Sanity checks
        if flavor == "market" and (limit_price is not None or stop_price is not None):
            raise ValueError("Market orders can't have limit/stop price specified")
        if flavor == "limit" and limit_price is None:
            raise ValueError("Limit orders must have limit price specified")
        if flavor == "stop" and stop_price is None:
            raise ValueError("Stop orders must have stop price specified")

        self._id = "{:032x}".format(random.getrandbits(128))
        self._symbol = symbol
        self._quantity = quantity
        self._flavor = self._check_flavor(flavor)
        self._date = date
        self._side = self._check_side(side)
        self._execution_time = None
        self._cancelled_time = None
        self._limit_price = limit_price
        self._stop_price = stop_price
        self._take_profit_price = take_profit_price
        self._stop_loss_price = stop_loss_price
        self._legs_by_id = dict()
        self._legs_by_type = dict()
        self._status = "new"
        self._replaces = None
        self._replaced_by = None
        self._linked_with = list()
        self._instrument_braket_order()

    def _check_side(self, side):
        sides = ["buy", "sell"]
        if side not in sides:
            raise ValueError("Order side must be of {}".format(sides))
        return side

    def _check_flavor(self, flavor):
        flavors = ["market", "limit", "stop", "take_profit", "stop_loss"]
        if flavor not in flavors:
            raise ValueError("Order flavor must one of {}".format(flavors))
        return flavor

    def _instrument_braket_order(self):
        take_profit_order = None
        stop_loss_order = None

        if self._take_profit_price is not None:
            log.debug("Creating take profit leg order")
            take_profit_order = Order(
                self.symbol,
                self.quantity,
                "sell" if self.side == "buy" else "buy",
                self.date,
                flavor="take_profit",
                limit_price=self._take_profit_price,
            )
            self._legs_by_id[take_profit_order.id] = take_profit_order
            self._legs_by_type[take_profit_order.flavor] = take_profit_order

        if self._stop_loss_price is not None:
            log.debug("Creating stop loss leg order")
            stop_loss_order = Order(
                self.symbol,
                self.quantity,
                "sell" if self.side == "buy" else "buy",
                self.date,
                flavor="stop_loss",
                stop_price=self._stop_loss_price,
            )
            self._legs_by_id[stop_loss_order.id] = stop_loss_order
            self._legs_by_type[stop_loss_order.flavor] = stop_loss_order

        if take_profit_order is not None and stop_loss_order is not None:
            log.debug("Linking take_profit and stop_loss orders")
            take_profit_order._linked_with.append(stop_loss_order)
            stop_loss_order._linked_with.append(take_profit_order)

    def promote(self):
        if self.flavor == "take_profit":
            log.debug(
                "Converting {} {} to limit order".format(self.symbol, self.flavor)
            )
            self.flavor = "limit"
        elif self._flavor == "stop_loss":
            log.debug("Converting {} {} to stop order".format(self.symbol, self.flavor))
            self.flavor = "stop"
        else:
            raise ValueError(
                "Can only promote {}/{} orders this is {}".format(
                    "take_profit", "stop_loss", self.flavor
                )
            )

    def get_stop_loss_order(self):
        if "stop_loss" in self._legs_by_type:
            return self._legs_by_type["stop_loss"]
        return None

    def get_take_profit_order(self):
        if "take_profit" in self._legs_by_type:
            return self._legs_by_type["take_profit"]
        return None

    def __str__(self):
        str_repr = "Order({}):\n".format(self.id)
        str_repr += " - symbol  : {}\n".format(self.symbol)
        str_repr += " - quantity: {}\n".format(self.quantity)
        str_repr += " - side    : {}\n".format(self.side)
        str_repr += " - flavor  : {}\n".format(self.flavor)
        str_repr += " - status  : {}\n".format(self.status)
        str_repr += " - time    : {}\n".format(self.date)
        str_repr += " - limit p.: {}\n".format(self.limit_price)
        str_repr += " - stop p. : {}\n".format(self.stop_price)
        leg = self.get_take_profit_order()
        if leg is not None:
            str_repr += " - take profit leg : {}\n".format(leg.id)
        leg = self.get_stop_loss_order()
        if self.get_stop_loss_order() is not None:
            str_repr += " - stop loss leg   : {}\n".format(leg.id)
        return str_repr

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, val):
        self._date = val

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val):
        self._status = val

    @property
    def side(self):
        return self._side

    @side.setter
    def side(self, val):
        self._side = val

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, val):
        self._symbol = val

    @property
    def limit_price(self):
        return self._limit_price

    @limit_price.setter
    def limit_price(self, val):
        self._limit_price = val

    @property
    def stop_price(self):
        return self._stop_price

    @stop_price.setter
    def stop_price(self, val):
        self._stop_price = val

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, val):
        self._quantity = val

    @property
    def flavor(self):
        return self._flavor

    @flavor.setter
    def flavor(self, val):
        self._flavor = val

    @property
    def take_profit_price(self):
        return self._take_profit_price

    @take_profit_price.setter
    def take_profit_price(self, val):
        self._take_profit_price = val

    @property
    def stop_loss_price(self):
        return self._stop_loss_price

    @stop_loss_price.setter
    def stop_loss_price(self, val):
        self._stop_loss_price = val

    @property
    def replaces(self):
        return self._replaces

    @replaces.setter
    def replaces(self, val):
        self._replaces = val

    @property
    def replaced_by(self):
        return self._replaced_by

    @replaced_by.setter
    def replaced_by(self, val):
        self._replaced_by = val

    def execute(
        self, price: float = None, execution_time: datetime = datetime.datetime.now()
    ):
        if self.status != "new":
            raise ValueError(
                "Cannot execute a order in status other than new \n{}".format(self)
            )

        # First we need to execute/convert the two leg orders
        leg = self.get_take_profit_order()
        if leg is not None:
            leg.execute()

        leg = self.get_stop_loss_order()
        if leg is not None:
            leg.execute()

        promotable_orders = ["take_profit", "stop_loss"]
        if self.flavor in promotable_orders:
            log.debug("Promoting {} order {}".format(self.flavor, self.id))
            self.promote()
            return None

        if self.flavor == "limit":
            price = self.limit_price
        elif self.flavor == "stop":
            # TODO this is a best case scenario, we need to make it a bit more relistic
            price = self.stop_price

        trade = Trade(self.symbol, self.quantity, price, self.side, execution_time)

        self.status = "executed"

        return trade

    def cancel(self, time: datetime = datetime.datetime.now()):
        self.status = "cancelled"

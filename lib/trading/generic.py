import datetime
from lib.util.logger import log


class Trade():

    def __init__(self, symbol: str, quantity: int, price: float, side: str, date: datetime):
        self._date = date
        self._side = side
        self._date = date
        self._price = price
        self._symbol = symbol
        self._quantity = quantity

    @property
    def date(self):
        return self._date

    @property
    def side(self):
        return self._side

    @property
    def price(self):
        return self._price

    @property
    def symbol(self):
        return self._symbol

    @property
    def quantity(self):
        return self._quantity

    @date.setter
    def date(self, val):
        self._date = val

    @side.setter
    def side(self, val):
        self._side = val

    @symbol.setter
    def symbol(self, val):
        self._symbol = val

    @price.setter
    def price(self, val):
        self._price = val

    @quantity.setter
    def quantity(self, val):
        self._quantity = val

    def __str__(self):
        str_repr = ""
        if self.side == "buy":
            str_repr += "Bought "
        else:
            str_repr += "Sold "
        str_repr += str(self.quantity) + " shares at " + \
            str(self.price) + "$ on " + str(self.date)
        return str_repr


class Position():

    def __init__(self, symbol: str, trade):
        self.side = "long" if trade.side == "buy" else "short"
        self.open_time = trade.date
        self.close_time = None
        self.symbol = symbol

        self.trades = [trade]
        self.leg_orders = {
            "take_profit": None,
            "stop_loss": None
        }

        # Batches will collect the current status whilst orders the
        # whole history
        self.batches = [{
            "quantity": trade.quantity,
            "price": trade.price
        }] if trade.side == "buy" else [{
            "quantity": -trade.quantity,
            "price": -trade.price
        }]

    def get_total_shares(self):
        total_shares = 0
        for batch in self.batches:
            total_shares += batch["quantity"]
        return total_shares

    def get_average_price(self):
        total_price = 0.0
        for batch in self.batches:
            total_price += batch["price"]
        return total_price / self.get_total_shares()

    def get_profit(self):
        pl = 0.0
        for t in self.trades:
            pl += ((t.price * t.quantity) if t.side ==
                   "buy" else -(t.price * t.quantity))

    def update_position(self, trade: Trade):
        if trade.symbol != self.symbol:
            log.error("Updating position for " + trade.symbol +
                      " but position is open for " + self.symbol)
            raise ValueError("Unexpected trade side: " + trade.side)

        if not self.is_open():
            log.error("Trying to update a closed position")
            raise ValueError("Trying to update a closed position")

        tradable_shares = abs(self.get_total_shares())
        if trade.side == "buy":
            if self.side == "long":
                self.batches.append({
                    "quantity": trade.quantity,
                    "price": trade.price
                })
            else:
                self._remove_shares(trade)
        elif trade.side == "sell":
            if self.side == "short":
                self.batches.append({
                    "quantity": -trade.quantity,
                    "price": -trade.price
                })
            else:
                self._remove_shares(trade)
        else:
            log.error("Unexpected trade side: " + trade.side)
            raise ValueError("Unexpected trade side: " + trade.side)

        self.trades.append(trade)

        if self.get_total_shares() == 0:
            log.info("Closing " + self.symbol + " " + self.side + " position ")

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
            self.batches = [
                batch for batch in self.batches if batch["quantity"] != 0]
        else:
            log.error("Invalid trade cannot " + trade.side +
                      " more than " + str(tradable_shares))
            raise ValueError(
                "Invalid trade cannot " + trade.side + " more than " + str(tradable_shares))

    def has_leg_orders(self):
        if self.leg_orders["take_profit"] != None:
            return True
        else:
            if self.leg_orders["stop_loss"] != None:
                return True

    def get_leg_orders(self):
        return self.leg_orders

    def get_average_entry_price(self):
        average_price = 0.0
        for batch in self.batches:
            average_price += (batch["quantity"] * batch["price"])
        return average_price / abs(self.get_total_shares())

    def is_open(self):
        return (False if len(self.batches) == 0 else True)

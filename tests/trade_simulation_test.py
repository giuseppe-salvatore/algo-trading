import time
import unittest
import datetime


# Project specific imports from lib
from lib.util.logger import log
from lib.trading.generic import Trade
from lib.trading.generic import Position

class TradeTest(unittest.TestCase):

    def test_buy_trade_creation(self):

        print("")
        log.info("Running   SimpleTradeTest - test_buy_trade_creation")

        date = datetime.datetime.now()
        side = "buy"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        buy = Trade(symbol, quantity, price, side, date)

        self.assertEqual(buy.date, date)
        log.info("Date correctly set")

        self.assertEqual(buy.side, side)
        log.info("Side correctly set")

        self.assertEqual(buy.price, price)
        log.info("Price correctly set")

        self.assertEqual(buy.symbol, symbol)
        log.info("Symbol correctly set")

        self.assertEqual(buy.quantity, quantity)
        log.info("Quantity correctly set")

        log.info("Completed SimpleTradeTest - test_buy_trade_creation")

    def test_sell_trade_creation(self):

        print("")
        log.info("Running   SimpleTradeTest - test_sell_trade_creation")

        date = datetime.datetime.now()
        side = "sell"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        sell = Trade(symbol, quantity, price, side, date)

        self.assertEqual(sell.date, date)
        log.info("Date correctly set")

        self.assertEqual(sell.side, side)
        log.info("Side correctly set")

        self.assertEqual(sell.price, price)
        log.info("Price correctly set")

        self.assertEqual(sell.symbol, symbol)
        log.info("Symbol correctly set")

        self.assertEqual(sell.quantity, quantity)
        log.info("Quantity correctly set")

        log.info("Completed SimpleTradeTest - test_sell_trade_creation")


class PositionTest(unittest.TestCase):

    def test_opening_long_position(self):
        print("")
        log.info("Running   PositionTest - test_opening_long_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "buy"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        buy = Trade(symbol, quantity, price, side, date)

        long_position = Position(symbol, buy)

        self.assertTrue(long_position.side == "long")
        log.info("Long position correctly created")

        log.info("Completed PositionTest - test_opening_long_position")

    def test_opening_short_position(self):
        print("")
        log.info("Running   PositionTest - test_opening_short_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "sell"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        sell = Trade(symbol, quantity, price, side, date)

        long_position = Position(symbol, sell)

        self.assertTrue(long_position.side == "short")
        log.info("Short position correctly created")

        log.info("Completed PositionTest - test_opening_short_position")

    def test_opening_long_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_opening_long_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "buy"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        buy = Trade(symbol, quantity, price, side, date)

        long_position = Position(symbol, buy)

        msg = "Opening a long position with "
        msg += str(long_position.batches[0]["quantity"]) + " shares"
        log.info(msg)
        self.assertTrue(long_position.batches[0]["quantity"] == quantity)
        log.info("Long position has correct quantity")
        log.info("Completed PositionTest - test_opening_long_position_quantity")

    def test_opening_short_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_opening_short_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "sell"
        price = 17.8
        symbol = "SPY"
        quantity = 10

        sell = Trade(symbol, quantity, price, side, date)

        long_position = Position(symbol, sell)

        msg = "Opening a short position with "
        msg += str(long_position.batches[0]["quantity"]) + " shares"
        log.info(msg)
        self.assertTrue(long_position.batches[0]["quantity"] == -quantity)
        log.info("Short position has correct quantity")
        log.info("Completed PositionTest - test_opening_short_position_quantity")

    def test_increasing_long_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_increasing_long_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "buy"
        price = 17.8
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 15

        buy1 = Trade(symbol, quantity1, price, side, date)
        buy2 = Trade(symbol, quantity2, price, side, date)

        long_position = Position(symbol, buy1)
        msg = "Opening a long position with "
        msg += str(long_position.batches[0]["quantity"]) + " shares"
        log.info(msg)
        long_position.update_position(buy2)
        log.info("Increasing long position by " + str(quantity2) + " shares at same price")

        self.assertTrue(long_position.get_total_shares() == (quantity1 + quantity2))
        msg = "Long position has been correctly increased at "
        msg += str(long_position.get_total_shares())
        log.info(msg)
        log.info("Completed PositionTest - test_increasing_long_position_quantity")

    def test_increasing_short_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_increasing_short_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "sell"
        price = 17.8
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 15

        sell1 = Trade(symbol, quantity1, price, side, date)
        sell2 = Trade(symbol, quantity2, price, side, date)

        position = Position(symbol, sell1)
        log.info("Opening a {} position with {} shares".format(
            position.side,
            position.batches[0]["quantity"]
        ))

        position.update_position(sell2)
        log.info("Increasing {} position by {} shares at same price".format(
            position.side,
            quantity2
        ))
        total_shares = position.get_total_shares()
        expected_shares = -(quantity1 + quantity2)

        self.assertTrue(total_shares == expected_shares)
        log.info("Short position has been correctly increased at {} ".format(
            total_shares
        ))

        log.info("Completed PositionTest - test_increasing_short_position_quantity")

    def test_increasing_long_position_average_price_check(self):
        print("")
        log.info(
            "Running   PositionTest - test_increasing_long_position_average_price_check")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "buy"
        price1 = 10.0
        price2 = 5.0
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        buy1 = Trade(symbol, quantity1, price1, side, date)
        buy2 = Trade(symbol, quantity2, price2, side, date)

        long_position = Position(symbol, buy1)
        log.info("Opening a long position with {} shares a {}$".format(
            long_position.batches[0]["quantity"],
            price1
        ))
        long_position.update_position(buy2)
        log.info("Increasing long position by {} shares a {}$".format(
            quantity2,
            price2
        ))

        expected_average_price = (
            (price1 * quantity1) + (price2 * quantity2)) / (quantity1 + quantity2)
        actual_average_price = long_position.get_average_entry_price()

        log.info("Expected average price {}$".format(expected_average_price))
        log.info("Actual average price {}$".format(actual_average_price))

        self.assertTrue(actual_average_price == expected_average_price)

        log.info("Long position average entry price is correct {}".format(
            long_position.get_average_entry_price()
        ))

        log.info("Completed PositionTest - test_increasing_long_position_average_price_check")

    def test_increasing_short_position_average_price_check(self):
        print("")
        log.info("Running   PositionTest - test_increasing_short_position_average_price_check")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        side = "sell"
        price1 = 10.0
        price2 = 5.0
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        sell1 = Trade(symbol, quantity1, price1, side, date)
        sell2 = Trade(symbol, quantity2, price2, side, date)

        long_position = Position(symbol, sell1)
        log.info("Opening a short position with " +
                 str(quantity1) + " shares at " + str(price1) + "$")
        long_position.update_position(sell2)
        log.info("Increasing short position by " +
                 str(quantity2) + " shares at " + str(price2) + "$")

        expected_average_price = (
            (price1 * quantity1) + (price2 * quantity2)) / (quantity1 + quantity2)
        log.info("Expected average price " + str(expected_average_price) + "$")
        log.info("Actual average price " +
                 str(long_position.get_average_entry_price()) + "$")
        self.assertTrue(long_position.get_average_entry_price()
                        == expected_average_price)
        log.info("Short position average entry price is correct " +
                 str(long_position.get_average_entry_price()))

        log.info(
            "Completed PositionTest - test_increasing_short_position_average_price_check")

    def test_list_trades_in_long_position(self):
        print("")
        log.info("Running   PositionTest - test_list_trades_in_long_position")

        # First we need a buy order to pass to the position
        symbol = "SPY"

        buy1 = Trade(symbol, 10, 10.0, "buy", datetime.datetime.now())
        time.sleep(.2)
        buy2 = Trade(symbol, 15, 5.0, "buy", datetime.datetime.now())
        time.sleep(.2)
        sell = Trade(symbol, 25, 10.0, "sell", datetime.datetime.now())

        position = Position(symbol, buy1)
        log.info("Opening a long position with " +
                 str(buy1.quantity) + " shares at " + str(buy1.price) + "$")
        position.update_position(buy2)
        log.info("Increasing long position by " +
                 str(buy2.quantity) + " shares at " + str(buy2.price) + "$")
        position.update_position(sell)
        log.info("Closing position")

        log.info("Expected number of trades = 3")
        self.assertTrue(len(position.trades) == 3)
        log.info("Correct number of trades")

        log.info("Trade 1: " + str(position.trades[0]))
        log.info("Trade 2: " + str(position.trades[1]))
        log.info("Trade 3: " + str(position.trades[2]))

        log.info("Completed PositionTest - test_list_trades_in_long_position")

    def test_list_trades_in_short_position(self):
        print("")
        log.info("Running   PositionTest - test_list_trades_in_short_position")

        # First we need a buy order to pass to the position
        symbol = "SPY"

        sell1 = Trade(symbol, 10, 10.0, "sell", datetime.datetime.now())
        time.sleep(.2)
        sell2 = Trade(symbol, 15, 5.0, "sell", datetime.datetime.now())
        time.sleep(.2)
        buy = Trade(symbol, 25, 10.0, "buy", datetime.datetime.now())

        position = Position(symbol, sell1)
        log.info("Opening a short position with " +
                 str(sell1.quantity) + " shares at " + str(sell1.price) + "$")
        position.update_position(sell2)
        log.info("Increasing short position by " +
                 str(sell2.quantity) + " shares at " + str(sell2.price) + "$")
        position.update_position(buy)
        log.info("Closing position")

        log.info("Expected number of trades = 3")
        self.assertTrue(len(position.trades) == 3)
        log.info("Correct number of trades")

        log.info("Trade 1: " + str(position.trades[0]))
        log.info("Trade 2: " + str(position.trades[1]))
        log.info("Trade 3: " + str(position.trades[2]))

        log.info("Completed PositionTest - test_list_trades_in_short_position")

    def test_closing_long_position(self):
        print("")
        log.info("Running   PositionTest - test_closing_long_position")

        # First we need a buy order to pass to the position
        symbol = "SPY"

        buy1 = Trade(symbol, 10, 10.0, "buy", datetime.datetime.now())
        buy2 = Trade(symbol, 15, 5.0, "buy", datetime.datetime.now())
        sell = Trade(symbol, 25, 10.0, "sell", datetime.datetime.now())

        position = Position(symbol, buy1)
        log.info("Opening a long position with " +
                 str(buy1.quantity) + " shares at " + str(buy1.price) + "$")
        position.update_position(buy2)
        log.info("Increasing long position by " +
                 str(buy2.quantity) + " shares at " + str(buy2.price) + "$")
        position.update_position(sell)
        log.info("Closing position")

        log.info("Expected total number of shares to be 0")
        log.info("Actual number of shares is " +
                 str(position.get_total_shares()))
        self.assertTrue(position.get_total_shares() == 0)
        log.info("Correct number of shares, position is closed")

        log.info("Completed PositionTest - test_closing_long_position")

    def test_closing_short_position(self):
        print("")
        log.info("Running   PositionTest - test_closing_short_position")

        # First we need a buy order to pass to the position
        symbol = "SPY"

        sell1 = Trade(symbol, 10, 10.0, "sell", datetime.datetime.now())
        time.sleep(.2)
        sell2 = Trade(symbol, 15, 5.0, "sell", datetime.datetime.now())
        time.sleep(.2)
        buy = Trade(symbol, 25, 10.0, "buy", datetime.datetime.now())

        position = Position(symbol, sell1)
        log.info("Opening a short position with " +
                 str(sell1.quantity) + " shares at " + str(sell1.price) + "$")
        position.update_position(sell2)
        log.info("Increasing short position by " +
                 str(sell2.quantity) + " shares at " + str(sell2.price) + "$")
        position.update_position(buy)
        log.info("Closing position")

        log.info("Expected total number of shares to be 0")
        log.info("Actual number of shares is " +
                 str(position.get_total_shares()))
        self.assertTrue(position.get_total_shares() == 0)
        log.info("Correct number of shares, position is closed")

        log.info("Completed PositionTest - test_closing_short_position")

    def test_decreasing_long_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_decreasing_long_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price = 17.8
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 5

        trade1 = Trade(symbol, quantity1, price, "buy", date)
        trade2 = Trade(symbol, quantity2, price, "sell", date)

        position = Position(symbol, trade1)
        log.info("Opening a long position with " +
                 str(position.batches[0]["quantity"]) + " shares")
        position.update_position(trade2)
        log.info("Decreasing long position by " +
                 str(quantity2) + " shares at same price")

        self.assertTrue(position.get_total_shares()
                        == (quantity1 - quantity2))
        log.info("Long position has been correctly decreased at " +
                 str(position.get_total_shares()))

        log.info("Completed PositionTest - test_decreasing_long_position_quantity")

    def test_decreasing_short_position_quantity(self):
        print("")
        log.info("Running   PositionTest - test_decreasing_short_position_quantity")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price = 17.8
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 5

        trade1 = Trade(symbol, quantity1, price, "sell", date)
        trade2 = Trade(symbol, quantity2, price, "buy", date)

        position = Position(symbol, trade1)
        log.info("Opening a short position with {} shares".format(
            position.batches[0]["quantity"]
        ))
        position.update_position(trade2)
        log.info("Decreasing short position by {} shares at same price".format(
            quantity2
        ))

        expected_shares = -(quantity1 - quantity2)
        actual_shares = position.get_total_shares()
        self.assertTrue(actual_shares == expected_shares)
        log.info("Short position has been correctly decreased at {}".format(
            position.get_total_shares()
        ))

        log.info("Completed PositionTest - test_decreasing_short_position_quantity")

    def test_profit_on_long_position(self):
        print("")
        log.info("Running   PositionTest - test_profit_on_long_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price1 = 10
        price2 = 15
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        trade1 = Trade(symbol, quantity1, price1, "buy", date)
        trade2 = Trade(symbol, quantity2, price2, "sell", date)

        position = Position(symbol, trade1)
        log.info("Opening a {} position with {} shares".format(
            position.side,
            position.batches[0]["quantity"]
        ))
        position.update_position(trade2)
        log.info("Closing {} position".format(position.side))

        actual_profit = position.get_profit()
        expected_profit = 50
        log.info("Expected profit: {}$\nActual profit: {}$".format(
            expected_profit,
            actual_profit
        ))
        self.assertTrue(expected_profit == actual_profit)

        log.info("Completed PositionTest - test_profit_on_long_position")

    def test_loss_on_long_position(self):
        print("")
        log.info("Running   PositionTest - test_loss_on_long_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price1 = 15
        price2 = 10
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        trade1 = Trade(symbol, quantity1, price1, "buy", date)
        trade2 = Trade(symbol, quantity2, price2, "sell", date)

        position = Position(symbol, trade1)
        log.info("Opening a {} position with {} shares".format(
            position.side,
            position.batches[0]["quantity"]
        ))
        position.update_position(trade2)
        log.info("Closing {} position".format(position.side))

        actual_profit = position.get_profit()
        expected_profit = -50
        log.info("Expected profit: {}$\nActual profit: {}$".format(
            expected_profit,
            actual_profit
        ))
        self.assertTrue(expected_profit == actual_profit)

        log.info("Completed PositionTest - test_loss_on_long_position")

    def test_profit_on_short_position(self):
        print("")
        log.info("Running   PositionTest - test_profit_on_short_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price1 = 15
        price2 = 10
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        trade1 = Trade(symbol, quantity1, price1, "sell", date)
        trade2 = Trade(symbol, quantity2, price2, "buy", date)

        position = Position(symbol, trade1)
        log.info("Opening a {} position with {} shares".format(
            position.side,
            position.batches[0]["quantity"]
        ))
        position.update_position(trade2)
        log.info("Closing {} position".format(position.side))

        actual_profit = position.get_profit()
        expected_profit = 50
        log.info("Expected profit: {}$\nActual profit: {}$".format(
            expected_profit,
            actual_profit
        ))
        self.assertTrue(expected_profit == actual_profit)

        log.info("Completed PositionTest - test_profit_on_long_position")

    def test_loss_on_short_position(self):
        print("")
        log.info("Running   PositionTest - test_loss_on_short_position")

        # First we need a buy order to pass to the position
        date = datetime.datetime.now()
        price1 = 10
        price2 = 15
        symbol = "SPY"
        quantity1 = 10
        quantity2 = 10

        trade1 = Trade(symbol, quantity1, price1, "sell", date)
        trade2 = Trade(symbol, quantity2, price2, "buy", date)

        position = Position(symbol, trade1)
        log.info("Opening a {} position with {} shares".format(
            position.side,
            position.batches[0]["quantity"]
        ))
        position.update_position(trade2)
        log.info("Closing {} position".format(position.side))

        actual_profit = position.get_profit()
        expected_profit = -50
        log.info("Expected profit: {}$\nActual profit: {}$".format(
            expected_profit,
            actual_profit
        ))
        self.assertTrue(expected_profit == actual_profit)

        log.info("Completed PositionTest - test_loss_on_short_position")

if __name__ == '__main__':
    unittest.main()

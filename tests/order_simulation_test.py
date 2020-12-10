# import time
import unittest
import datetime

# Project specific imports from lib
# from lib.util.logger import log
from lib.trading.platform import SimulationPlatform, TradingPlatform
from lib.trading.generic import Trade, Order, Position, TradeSession, Candle


class MarketOrderTest(unittest.TestCase):
    '''
    Assessing the functional behaviour for Market Orders as standalone objects
    '''

    def test_default_buy_order_is_market(self):
        '''
        We test that the default buy order flavor is market and all the properties
        are correctly assigned and accessible
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        order = Order(symbol, quantity, side, date)

        self.assertEqual(order.symbol, symbol)
        self.assertEqual(order.quantity, quantity)
        self.assertEqual(order.date, date)
        self.assertEqual(order.side, side)

    def test_default_sell_order_is_market(self):
        '''
        We test that the default sell order flavor is market and all the properties
        are correctly assigned and accessible
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "sell"
        quantity = 10

        order = Order(symbol, quantity, side, date)

        self.assertEqual(order.symbol, symbol)
        self.assertEqual(order.quantity, quantity)
        self.assertEqual(order.date, date)
        self.assertEqual(order.side, side)

    def test_unknowng_order_side_triggers_exceprtion(self):
        '''
        Testing an unknown order side should trigger an exception
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        quantity = 10

        self.assertRaises(ValueError,
                          Order,
                          symbol, quantity, "beep boop", date)

    def test_explicit_market_order(self):
        '''
        Testing the explicit side field is correctly set
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        quantity = 10

        order = Order(symbol, quantity, "buy", date, flavor='market')
        self.assertEqual(order.flavor, 'market')
        order = Order(symbol, quantity, "sell", date, flavor='market')
        self.assertEqual(order.flavor, 'market')

    def test_generated_order_id_lenght(self):
        '''
        Testing the order id is automatically generated and the expected lenght
        '''
        order = Order("TEST", 1, "buy", datetime.datetime.now())
        self.assertTrue(len(order.id) == 32)
        order = Order("TEST", 1, "sell", datetime.datetime.now())
        self.assertTrue(len(order.id) == 32)

    def test_market_rejects_limit_field(self):
        '''
        Testing an exception is thrown if a market order has a limit field set
        '''
        order = Order("TEST", 1, "buy", datetime.datetime.now())
        self.assertTrue(len(order.id) == 32)
        order = Order("TEST", 1, "sell", datetime.datetime.now())
        self.assertTrue(len(order.id) == 32)

    def test_market_rejects_stop_field(self):
        '''
        Testing an exception is thrown if a market order has a stop field set
        '''
        now = datetime.datetime.now()
        self.assertRaises(ValueError,
                          Order,
                          symbol="TEST", quantity=1, side="buy", date=now, limit_price=10)

        self.assertRaises(ValueError,
                          Order,
                          symbol="TEST", quantity=1, side="sell", date=now, limit_price=10)

        self.assertRaises(ValueError,
                          Order,
                          symbol="TEST", quantity=1, flavor='market',
                          side="buy", date=now, stop_price=10)

        self.assertRaises(ValueError,
                          Order,
                          symbol="TEST", quantity=1, flavor='market',
                          side="sell", date=now, stop_price=10)


class LimitOrderTest(unittest.TestCase):

    def test_explicit_limit_order(self):
        '''
        Testing the fields is correctly set and accessible
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        quantity = 10

        order = Order(symbol, quantity, "buy", date, flavor='limit', limit_price=10)
        self.assertEqual(order.flavor, 'limit')
        order = Order(symbol, quantity, "sell", date, flavor='limit', limit_price=10)
        self.assertEqual(order.flavor, 'limit')

    def test_exception_if_missing_limit_price(self):
        '''
        Testing exception when no limit price is provided on limit orders
        '''
        date = datetime.datetime.now()
        symbol = "SPY"
        quantity = 10

        self.assertRaises(ValueError,
                          Order,
                          symbol, quantity, "buy", date, flavor='limit')

        self.assertRaises(ValueError,
                          Order,
                          symbol, quantity, "sell", date, flavor='limit')

    def test_buy_market_braket_creates_order_with_both_legs(self):

        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        order = Order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='market',
            take_profit_price=20.0,
            stop_loss_price=5.0
        )
        print(len(order._legs_by_id))
        print(len(order._legs_by_type))
        self.assertTrue(len(order._legs_by_id) == 2)
        self.assertTrue(len(order._legs_by_type) == 2)
        print(order)

        leg_order: Order = order.get_take_profit_order()
        self.assertTrue(len(leg_order.id) == 32)
        self.assertTrue(leg_order.flavor == 'take_profit')
        self.assertTrue(leg_order.limit_price == 20.0)
        print(leg_order)

        leg_order: Order = order.get_stop_loss_order()
        self.assertTrue(len(leg_order.id) == 32)
        self.assertTrue(leg_order.flavor == 'stop_loss')
        self.assertTrue(leg_order.stop_price == 5.0)
        print(leg_order)

    def test_buy_market_braket_creates_order_with_take_profit_leg(self):
        pass

    def test_buy_market_braket_creates_order_with_stop_loss_leg(self):
        pass

    def test_buy_limit_braket_creates_order_with_both_legs(self):
        pass

    def test_buy_stop_braket_creates_order_with_both_leg(self):
        pass

    def test_buy_market_order_execution(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        order = Order(
            symbol,
            quantity,
            side,
            date,
            flavor='market')

        results = order.execute(10.0)
        self.assertEqual(type(results[0]), Trade)
        # Execution of a simple market order only generates one trade that is the first element of
        # the list, the other 2 are for the legs order that get translated to limit and/or stop
        # orders
        self.assertEqual(results[1], None)
        self.assertEqual(results[2], None)
        trade: Trade = results[0]
        self.assertEqual(trade.symbol, symbol)
        self.assertEqual(trade.quantity, quantity)
        self.assertEqual(trade.side, side)

    def test_sell_market_order_execution(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "sell"
        quantity = 10

        order = Order(
            symbol,
            quantity,
            side,
            date,
            flavor='market')

        results = order.execute(15)
        self.assertEqual(type(results[0]), Trade)
        trade: Trade = results[0]
        self.assertEqual(results[1], None)
        self.assertEqual(results[2], None)
        self.assertEqual(trade.symbol, symbol)
        self.assertEqual(trade.quantity, quantity)
        self.assertEqual(trade.side, side)


class SimulationTradingPlatformTest(unittest.TestCase):

    def test_trading_platorm_get(self):
        platform: SimulationPlatform = TradingPlatform.get_trading_platform("simulation")
        self.assertTrue(platform is not None)
        self.assertEqual(type(platform), SimulationPlatform)

    def test_trading_platorm_get_error(self):
        self.assertRaises(ValueError,
                          TradingPlatform.get_trading_platform,
                          "unknown")

    def test_market_order_creation_and_execution(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(date, {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='market'
        )

        self.assertTrue(len(id) == 32)
        self.assertTrue(id in platform.executed_orders)
        self.assertEqual(platform.executed_orders[id].status, 'executed')

    def test_market_order_execution_creates_position(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='market'
        )

        self.assertTrue(platform.trading_session.get_current_position("SPY").is_open())

    def test_submit_bracket_limit_order_adds_legs_to_active_orders(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10.0
        take_profit = 20.0
        stop_loss = 5.0

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(date, {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='limit',
            limit_price=10.0,
            take_profit_price=take_profit,
            stop_loss_price=stop_loss
        )

        bracket_order: Order = platform.active_orders[id]
        take_profit_order = bracket_order.get_take_profit_order()
        stop_loss_order = bracket_order.get_stop_loss_order()

        self.assertTrue(take_profit_order.id in platform.active_orders)
        self.assertTrue(stop_loss_order.id in platform.active_orders)

    def test_submit_bracket_stop_order_adds_legs_to_active_orders(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10.0
        take_profit = 20.0
        stop_loss = 5.0

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(date, {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='stop',
            stop_price=10.0,
            take_profit_price=take_profit,
            stop_loss_price=stop_loss
        )

        bracket_order: Order = platform.active_orders[id]
        take_profit_order = bracket_order.get_take_profit_order()
        stop_loss_order = bracket_order.get_stop_loss_order()

        self.assertTrue(take_profit_order.id in platform.active_orders)
        self.assertEqual(platform.active_orders[take_profit_order.id].status, 'new')
        self.assertTrue(stop_loss_order.id in platform.active_orders)
        self.assertEqual(platform.active_orders[take_profit_order.id].status, 'new')

    def test_bracket_order_take_profit_leg_is_valid(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10.0
        take_profit_price = 9.0

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(date, {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))
        self.assertRaises(ValueError,
                          platform.submit_order,
                          symbol=symbol,
                          quantity=quantity,
                          side=side,
                          date=date,
                          flavor='market',
                          take_profit_price=take_profit_price
                          )

    def test_limit_bracket_order_creation_and_execution(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10.0
        take_profit_price = 20.0
        stop_loss_price = 5.0

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(date, {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='limit',
            limit_price=10.0,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price
        )

        # After submitting a limit/stop order with legs we want to make sure that
        # also the leg orders are active, the will triggered/executed (which means converted)
        # when the parent order is executed
        self.assertTrue(len(id) == 32)
        self.assertTrue(id in platform.active_orders)
        self.assertEqual(platform.active_orders[id].status, 'new')
        original_limit_order: Order = platform.active_orders[id]
        self.assertIsNotNone(original_limit_order)

        # Checking the take profit leg order
        take_profit_order: Order = original_limit_order.get_take_profit_order()
        self.assertEqual(take_profit_order.status, 'new')
        self.assertEqual(take_profit_order.flavor, 'take_profit')
        self.assertEqual(take_profit_order.limit_price, take_profit_price)

        # Checking the stop loss leg order
        stop_loss_order: Order = original_limit_order.get_stop_loss_order()
        self.assertEqual(stop_loss_order.status, 'new')
        self.assertEqual(stop_loss_order.flavor, 'stop_loss')
        self.assertEqual(stop_loss_order.stop_price, stop_loss_price)

        platform.print_all_orders()

        # Order execution (note that with market order this transition is immediate)
        platform._execute_order(id)
        self.assertTrue(id in platform.executed_orders)
        self.assertEqual(platform.executed_orders[id].status, 'executed')

        # An executed market braket order triggers the creation of other orders depending
        # on the leg orders that exist. Take profit order is converted to limit order and
        # stop loss order is converted to stop order. But to access the limit and stop
        # orders we either have the ids already or we need to go through the active order
        # or access the braket order, get the take profit (resp: stop loss) and access via
        # the replaced_by field
        braket: Order = platform.executed_orders[id]
        limit_id = braket.get_take_profit_order().replaced_by
        limit: Order = platform.active_orders[limit_id]
        self.assertEqual(type(limit), Order)
        self.assertEqual(limit.flavor, 'limit')
        self.assertIsNotNone(limit.limit_price)
        stop_id = braket.get_stop_loss_order().replaced_by
        stop: Order = platform.active_orders[stop_id]
        self.assertEqual(type(stop), Order)
        self.assertEqual(stop.flavor, 'stop')
        self.assertIsNotNone(stop.stop_price)
        self.assertIsNotNone(braket)

        platform.print_all_orders()

        self.assertIsNotNone(limit)
        self.assertEqual(limit.symbol, "SPY")
        self.assertEqual(limit.side, "sell")
        self.assertEqual(limit.flavor, "limit")
        # limit replaces the take_profit
        self.assertIsNotNone(limit.replaces)
        take_profit = platform.get_order(limit.replaces)
        self.assertEqual(take_profit.status, 'executed')
        self.assertTrue(take_profit.id in platform.executed_orders)

        self.assertIsNotNone(stop)
        self.assertEqual(stop.symbol, "SPY")
        self.assertEqual(stop.side, "sell")
        self.assertEqual(stop.flavor, "stop")
        # stop replaces the stop_loss
        self.assertIsNotNone(stop.replaces)
        stop_loss = platform.get_order(stop.replaces)
        self.assertEqual(stop_loss.status, 'executed')
        self.assertTrue(stop_loss.id in platform.executed_orders)

    def test_limit_order_activation(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='limit',
            limit_price=10
        )

        self.assertTrue(len(id) == 32)
        self.assertTrue(id in platform.active_orders)
        self.assertEqual(platform.active_orders[id].status, 'new')

    def test_buy_limit_order_triggers_on_high(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 12,
                "open": 12,
                "close": 12,
                "low": 12,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='limit',
            limit_price=10
        )

        self.assertTrue(id in platform.active_orders)
        self.assertTrue(id not in platform.executed_orders)
        self.assertEqual(platform.active_orders[id].status, 'new')

        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 11,
                "open": 11,
                "close": 11,
                "low": 11,
                "volume": 1000
            }))
        self.assertTrue(id in platform.active_orders)
        self.assertTrue(id not in platform.executed_orders)

        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 10,
                "open": 10,
                "close": 10,
                "low": 10,
                "volume": 1000
            }))

        self.assertTrue(id not in platform.active_orders)
        self.assertTrue(id in platform.executed_orders)
        order = platform.get_order(id)
        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'executed')

    def test_stop_order_activation(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='stop',
            stop_price=5
        )

        self.assertTrue(len(id) == 32)
        self.assertTrue(id in platform.active_orders)
        self.assertEqual(platform.active_orders[id].status, 'new')

    def test_market_order_cancellation(self):
        date = datetime.datetime.now()
        symbol = "SPY"
        side = "buy"
        quantity = 10

        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol=symbol,
            quantity=quantity,
            side=side,
            date=date,
            flavor='limit',
            limit_price=10
        )

        self.assertTrue(len(id) == 32)
        self.assertTrue(id in platform.active_orders)
        self.assertEqual(platform.active_orders[id].status, 'new')

        platform.cancel_order(id)
        self.assertTrue(id in platform.cancelled_orders)
        self.assertTrue(id not in platform.active_orders)
        self.assertEqual(platform.cancelled_orders[id].status, 'cancelled')

    def test_inactive_order_execution_raises_error(self):
        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol="SPY",
            quantity=10,
            side="buy",
            date=datetime.datetime.now(),
            flavor='limit',
            limit_price=10
        )
        platform.cancel_order(id)
        self.assertRaises(ValueError,
                          platform._execute_order,
                          id)


class TradingPlatformTest(unittest.TestCase):

    def test_get_orders(self):
        platform = SimulationPlatform()
        platform.tick(
            "SPY",
            Candle(datetime.datetime.now(), {
                "high": 7,
                "open": 7,
                "close": 7,
                "low": 7,
                "volume": 1000
            }))
        id = platform.submit_order(
            symbol="SPY",
            quantity=10,
            side="buy",
            date=datetime.datetime.now(),
            flavor='limit',
            limit_price=10
        )
        active_order: Order = platform.get_order(id)
        platform.cancel_order(id)
        cancelled_order: Order = platform.get_order(id)
        self.assertEqual(active_order, cancelled_order)

    def test_get_not_submitted_order(self):
        platform = SimulationPlatform()
        order = Order(
            symbol="SPY",
            quantity=10,
            side="buy",
            date=datetime.datetime.now(),
            flavor='limit',
            limit_price=10
        )
        not_submitted_order: Order = platform.get_order(order.id)
        self.assertIsNone(not_submitted_order)

    def test_get_not_submitted_order(self):
        platform = SimulationPlatform()
        order = Order(
            symbol="SPY",
            quantity=10,
            side="buy",
            date=datetime.datetime.now(),
            flavor='limit',
            limit_price=10
        )
        not_submitted_order: Order = platform.get_order(order.id)
        self.assertIsNone(not_submitted_order)

    def test_cancel_unexisting_order_throws_error(self):
        platform = SimulationPlatform()
        order = Order(
            symbol="SPY",
            quantity=10,
            side="buy",
            date=datetime.datetime.now(),
            flavor='limit',
            limit_price=10
        )

        self.assertRaises(
            ValueError,
            platform.cancel_order,
            order.id)

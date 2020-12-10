from datetime import datetime
from lib.trading.platform import Order, TradingPlatform, SimulationPlatform, Candle
from pytest_bdd import scenario, given, when, then

trading_platform: SimulationPlatform = TradingPlatform.get_trading_platform("simulation")
submitted_limit_order_id = None
submitted_market_order_id = None

@scenario('../features/orders.feature', 'Placing a bracket limit order')
def test_bracket_limit_order():
    pass

@scenario('../features/orders.feature', 'Placing a bracket market order')
def test_bracket_market_order():
    pass

@given("I submit a bracket market order to buy 10 AAPL stocks")
def place_braket_market_order():
    global submitted_market_order_id
    trading_platform.clear()
    candle = Candle(
        datetime.now(),
        {
            "high": 10,
            "low": 10,
            "open": 10,
            "close": 10,
            "volume": 5000,
        }
    )
    trading_platform.tick("AAPL", candle)
    submitted_market_order_id = trading_platform.submit_order(
        symbol='AAPL',
        quantity=10,
        side='buy',
        flavor='market',
        date=datetime.now(),
        take_profit_price=15,
        stop_loss_price=8)

@when("the stock price goes above the limit price")
def price_above_limit_price():
    candle = Candle(
        datetime.now(),
        {
            "high": 16,
            "low": 11,
            "open": 10,
            "close": 14,
            "volume": 5000,
        }
    )
    trading_platform.tick("AAPL", candle)

@then("the limit leg order is executed")
def the_limit_order_is_executed():
    market_order: Order = trading_platform.get_order(submitted_market_order_id)
    take_profit_id = market_order.get_take_profit_order()
    assert take_profit_id is not None
    assert take_profit_id.id in trading_platform.executed_orders
    assert take_profit_id.id not in trading_platform.active_orders
    assert take_profit_id.status == 'executed'

@then("the position is closed")
def the_position_is_closed():
    positions = trading_platform.trading_session.get_positions('AAPL')
    assert positions[0].is_open() is False

@then("the stop order is cancelled")
def the_stop_order_is_cancelled():
    market_order: Order = trading_platform.get_order(submitted_market_order_id)
    stop_order = market_order.get_stop_loss_order()
    assert stop_order is not None
    assert len(stop_order._linked_with) > 0
    assert stop_order.status == 'cancelled'
    assert stop_order.id in trading_platform.cancelled_orders
    assert stop_order.id not in trading_platform.active_orders

@given("I submit a bracket limit order to buy 10 AAPL stocks")
def place_braket_limit_order():
    global submitted_limit_order_id
    trading_platform.clear()
    candle = Candle(
        datetime.now(),
        {
            "high": 10,
            "low": 10,
            "open": 10,
            "close": 10,
            "volume": 5000,
        }
    )
    trading_platform.tick("AAPL", candle)
    submitted_limit_order_id = trading_platform.submit_order(
        symbol='AAPL',
        quantity=10,
        side='buy',
        flavor='limit',
        date=datetime.now(),
        limit_price=10,
        take_profit_price=15,
        stop_loss_price=8)

@when("the limit price is hit")
def the_limit_price_is_hit():
    return True

@then("the order is executed")
def execute_order():
    trading_platform._execute_order(order_id=submitted_limit_order_id)

@given("a long position with 10 AAPL is open")
@then("a long position with 10 AAPL is open")
def check_position():
    positions = trading_platform.trading_session.get_positions('AAPL')
    assert positions[0] is not None
    assert positions[0].symbol == 'AAPL'

@then("the take profit leg is coverted in a limit order")
def check_take_profit_order():
    submitted_limit_order: Order = trading_platform.get_order(submitted_limit_order_id)
    take_profit_order: Order = submitted_limit_order.get_take_profit_order()
    assert take_profit_order is not None
    assert take_profit_order.flavor == "limit"

@then("the stop loss leg is converted in a stop order")
def check_stop_loss_order():
    submitted_limit_order = trading_platform.get_order(submitted_limit_order_id)
    stop_loss_order: Order = submitted_limit_order.get_stop_loss_order()
    assert stop_loss_order is not None
    assert stop_loss_order.flavor == "stop"

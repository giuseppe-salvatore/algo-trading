from datetime import datetime
from lib.trading.platform import Order, TradingPlatform, SimulationPlatform
from pytest_bdd import scenario, given, when, then

trading_platform: SimulationPlatform = TradingPlatform.get_trading_platform("simulation")
submitted_limit_order_id = None

@scenario('../features/orders.feature', 'Placing a bracket limit order')
def test_publish():
    pass

@given("I place a bracket limit order to buy 10 AAPL stocks")
def place_order():
    global submitted_limit_order_id
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

@then("a long position with 10 AAPL is open")
def check_position():
    positions = trading_platform.trading_session.get_positions('AAPL')
    assert positions[0] is not None
    assert positions[0].symbol == 'AAPL'

@then("the take profit leg is coverted in a limit order")
def check_take_profit_order():
    submitted_limit_order: Order = trading_platform.get_order(submitted_limit_order_id)
    take_profit_order: Order = submitted_limit_order.get_take_profit_order()
    limit_order: Order = trading_platform.get_order(take_profit_order.replaced_by)
    assert limit_order is not None
    assert limit_order.replaces == take_profit_order.id

@then("the stop loss leg is converted in a stop order")
def check_stop_loss_order():
    submitted_limit_order = trading_platform.get_order(submitted_limit_order_id)
    stop_loss_order: Order = submitted_limit_order.get_stop_loss_order()
    stop_order: Order = trading_platform.get_order(stop_loss_order.replaced_by)
    assert stop_order is not None
    assert stop_order.replaces == stop_loss_order.id

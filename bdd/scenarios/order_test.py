from datetime import datetime
from lib.trading.platform import Order, TradingPlatform, SimulationPlatform, Candle
from pytest_bdd import scenario, given, when, then, parsers

trading_platform: SimulationPlatform = TradingPlatform.get_trading_platform(
    "simulation")
submitted_limit_order_id = None
submitted_market_order_id = None
got_value_error = False
order_id = None


@scenario('../features/orders.feature', 'Placing a bracket limit order')
def test_bracket_limit_order():
    pass

@scenario('../features/orders.feature', 'Placing a bracket market order')
def test_bracket_market_order():
    pass

@scenario('../features/orders.feature', 'Placing a buy market order above the available cash balance')
def test_buy_order_above_balance():
    pass

@scenario('../features/orders.feature', 'Placing a buy market order below the available cash balance')
def test_buy_order_below_balance():
    pass

@scenario('../features/orders.feature', 'Placing a sell market order below the available cash balance')
def test_sell_order_below_balance():
    pass

@given("I submit a bracket market order to buy 10 AAPL stocks")
def place_bracket_market_order():
    global submitted_market_order_id
    trading_platform.clear()
    trading_platform.deposit(10000)
    candle = Candle(datetime.now(), {
        "high": 10,
        "low": 10,
        "open": 10,
        "close": 10,
        "volume": 5000,
    })
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
    candle = Candle(datetime.now(), {
        "high": 16,
        "low": 11,
        "open": 10,
        "close": 14,
        "volume": 5000,
    })
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
def place_bracket_limit_order():
    global submitted_limit_order_id
    trading_platform.clear()
    trading_platform.deposit(10000)
    candle = Candle(datetime.now(), {
        "high": 10,
        "low": 10,
        "open": 10,
        "close": 10,
        "volume": 5000,
    })
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


@then("the take profit leg is converted in a limit order")
def check_take_profit_order():
    submitted_limit_order: Order = trading_platform.get_order(
        submitted_limit_order_id)
    take_profit_order: Order = submitted_limit_order.get_take_profit_order()
    assert take_profit_order is not None
    assert take_profit_order.flavor == "limit"


@then("the stop loss leg is converted in a stop order")
def check_stop_loss_order():
    submitted_limit_order = trading_platform.get_order(
        submitted_limit_order_id)
    stop_loss_order: Order = submitted_limit_order.get_stop_loss_order()
    assert stop_loss_order is not None
    assert stop_loss_order.flavor == "stop"

@given(parsers.parse("no open positions with {symbol}"))
def check_no_open_positions_for_symbol(symbol):
    position = trading_platform.trading_session.get_current_position(symbol)
    assert position is None

@given(parsers.parse("I have {amount}$ available in my cash balance"))
def set_initial_balance(amount):
    trading_platform.clear()
    trading_platform.deposit(int(amount))

@given(parsers.parse("the {symbol} stock price is {unit_price}$ per unit"))
def set_stock_price(symbol, unit_price):
    unit_price = int(unit_price)
    candle = Candle(datetime.now(), {
        "high": unit_price,
        "low": unit_price,
        "open": unit_price,
        "close": unit_price,
        "volume": 5000,
    })
    trading_platform.tick(symbol, candle)

@when(parsers.parse("I submit a market buy order for {quantity} {symbol} stocks"))
def place_market_buy_order(quantity, symbol):
    global got_value_error
    global order_id
    try:
        order_id = trading_platform.submit_order(
            symbol=symbol,
            quantity=int(quantity),
            side='buy',
            flavor='market',
            date=datetime.now())
    except Exception:
        got_value_error = True

@when(parsers.parse("I submit a market sell order for {quantity} {symbol} stocks"))
def place_market_sell_order(quantity, symbol):
    global got_value_error
    global order_id
    try:
        order_id = trading_platform.submit_order(
            symbol=symbol,
            quantity=int(quantity),
            side='sell',
            flavor='market',
            date=datetime.now())
    except Exception:
        got_value_error = True

@then("the order should be rejected")
def order_is_rejected():
    global got_value_error
    assert got_value_error is True
    assert order_id is None

@then("the order should be executed")
def order_is_executed():
    global got_value_error
    assert got_value_error is True
    assert order_id is not None
    assert type(order_id) is str

@then(parsers.parse("my cash balance should be {amount}$"))
def check_cash_balance(amount):
    assert trading_platform.available_cash == int(amount)

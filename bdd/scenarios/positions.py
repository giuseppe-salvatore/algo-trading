from datetime import datetime
from lib.trading.platform import TradingPlatform, SimulationPlatform, Candle
from pytest_bdd import scenario, given, when, then, parsers
from lib.trading.generic import Position
from lib.util.logger import log

start_time = datetime(2000, 1, 1, 12, 0)
curr_time = 0

def get_curr_time():
    global curr_time
    curr_date = datetime(2000, 1, 1, 12, curr_time)
    curr_time += 1
    return curr_date


def get_next_time():
    global curr_time
    curr_time += 1
    return datetime(2000, 1, 1, 12, curr_time)


trading_platform: SimulationPlatform = TradingPlatform.get_trading_platform("simulation")


@scenario(
    "../features/positions.feature", "No positions are open when the simulation starts"
)
def test_no_position_open():
    pass


@scenario(
    "../features/positions.feature", "A market buy order opens a long position"
)
def test_long_position_open():
    pass


@scenario(
    "../features/positions.feature", "A market sell order opens a short position"
)
def test_short_position_open():
    pass


@scenario(
    "../features/positions.feature", "A market sell order on a long position for same quantity, closes the position"
)
def test_long_position_closes():
    pass


@scenario(
    "../features/positions.feature", "A market buy order on a short position for same quantity, closes the position"
)
def test_short_position_closes():
    pass


@scenario(
    "../features/positions.feature", "Equity doesn't change when no positions are open"
)
def test_equity_does_not_change():
    pass


@scenario("../features/positions.feature", "Equity gets updated when a position is open")
def test_equity_changes():
    pass


@scenario("../features/positions.feature", "Equity is not updated when a position is already closed")
def test_equity_does_not_get_updated_when_a_position_is_closed():
    pass


@scenario("../features/positions.feature", "Equity goes back to balance when a position decreased")
def test_equity_goes_back_to_balance_when_a_position_is_decreased():
    pass

@scenario("../features/positions.feature", "Equity moves with market value")
def test_equity_moves_with_market_value():
    pass

@scenario("../features/positions.feature", "Equity goes back to balance when a position is liquidated")
def test_goes_back_to_balance_when_a_position_is_liquidated():
    pass

@given("I start a new trading session")
def start_trading_session():
    global curr_time
    trading_platform.clear()
    curr_time = 0


@given(parsers.parse("I deposit {amount}$"))
def deposit(amount):
    trading_platform.deposit(int(amount))


@given(parsers.parse("I have a {side} position of {quantity} {sym} stocks bought at {price}$"))
def open_a_position(sym, side, quantity, price):
    price = float(price)
    stock_price_set(sym, price)
    if side == "long":
        direction = "buy"
    else:
        direction = "sell"
    trading_platform.submit_order(
        symbol=sym,
        quantity=int(quantity),
        side=direction,
        flavor='market',
        date=get_curr_time())
    position_is_open("long", sym)


@then("no positions should be open")
@given("no open positions with AAPL")
@given("there are no open positions")
def no_positions_open():
    positions = trading_platform.trading_session.get_symbols()
    assert len(positions) == 0


@given(parsers.parse("I submit a market {direction} order for {quantity} {symbol} stocks"))
@when(parsers.parse("I submit a market {direction} order for {quantity} {symbol} stocks"))
def submit_market_order(direction, quantity, symbol):
    curr_time = get_curr_time()
    candle = Candle(curr_time, {
        "high": 10,
        "low": 10,
        "open": 10,
        "close": 10,
        "volume": 5000,
    })
    trading_platform.tick(symbol, candle)
    submitted_market_order_id = trading_platform.submit_order(
        symbol=symbol,
        quantity=int(quantity),
        side=direction,
        flavor='market',
        date=curr_time)
    assert submitted_market_order_id is not None
    assert type(submitted_market_order_id) is str
    assert submitted_market_order_id != ""

@when(parsers.parse("the {sym} price moves to {price}$"))
def stock_price_set(sym, price):
    price = float(price)
    candle = Candle(get_curr_time(), {
        "high": price,
        "low": price,
        "open": price,
        "close": price,
        "volume": 5000,
    })
    trading_platform.tick(sym, candle)


@when("the plaform moves to the next candle")
def platform_moves():
    candle = Candle(get_curr_time(), {
        "high": 20,
        "low": 20,
        "open": 20,
        "close": 20,
        "volume": 5000,
    })
    trading_platform.tick("AAPL", candle)
    candle = Candle(get_curr_time(), {
        "high": 21,
        "low": 21,
        "open": 21,
        "close": 21,
        "volume": 5000,
    })
    trading_platform.tick("AAPL", candle)


@when("I close the position")
def close_position():
    pos = trading_platform.trading_session.get_current_position("AAPL")
    pos.liquidate(21, get_curr_time())

@when(parsers.parse("I sell {quantity} {sym} stocks"))
def i_sell_stocks(sym, quantity):
    trading_platform.submit_order(
        symbol=sym,
        quantity=int(quantity),
        side="sell",
        flavor='market',
        date=get_curr_time())

@then(parsers.parse("my cash balance should be {amount}$"))
def my_cash_balance_should_be(amount):
    assert trading_platform.available_cash == float(amount)


@then("my equity should not have been updated")
def equity_not_updated():
    assert False


@then(parsers.parse("a {side} position for {symbol} should be open"))
def position_is_open(side, symbol):
    curr_pos: Position = trading_platform.trading_session.get_current_position(symbol=symbol)
    assert curr_pos is not None
    assert curr_pos.symbol == symbol
    assert curr_pos.side == side
    assert curr_pos.is_open() is True


@then(parsers.parse("the {symbol} position should be closed"))
def position_is_closed(symbol):
    curr_pos: Position = trading_platform.trading_session.get_current_position(symbol)
    assert curr_pos is None
    latest_pos: Position = trading_platform.trading_session.get_positions(symbol)[-1]
    assert latest_pos.is_open() is False


@then(parsers.parse("my equity should be {amount}$"))
def my_equity_should_be(amount):
    equity = trading_platform.get_equity()
    if len(equity.keys()) == 0:
        assert True
    assert int(amount) == 0


@then(parsers.parse("my equity should update to {value}$"))
def my_equity_should_be_updated(value):
    eq = trading_platform.get_equity()
    log.debug(eq)

    if len(eq) == 0:
        raise Exception("Can't validate equity value as there are none present")
    latest_time = None
    for el in eq.keys():
        if latest_time is None:
            latest_time = el
        else:
            if el > latest_time:
                latest_time = el

    assert trading_platform.get_equity()[latest_time]["value"] == float(value)

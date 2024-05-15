from datetime import datetime
from lib.trading.platform import TradingPlatform, SimulationPlatform, Candle
from pytest_bdd import scenario, given, when, then, parsers
from lib.trading.generic import Position

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


@given("I start a new trading session")
def start_trading_session():
    trading_platform.clear()


@given(parsers.parse("I deposit {amount}$"))
def deposit(amount):
    trading_platform.deposit(int(amount))


@then("no positions should be open")
@given("no open positions with AAPL")
def no_positions_open():
    positions = trading_platform.trading_session.get_symbols()
    assert len(positions) == 0


@given(parsers.parse("I submit a market {direction} order for {quantity} {symbol} stocks"))
@when(parsers.parse("I submit a market {direction} order for {quantity} {symbol} stocks"))
def submit_market_order(direction, quantity, symbol):
    candle = Candle(datetime.now(), {
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
        date=datetime.now())
    assert submitted_market_order_id is not None
    assert type(submitted_market_order_id) is str
    assert submitted_market_order_id != ""


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

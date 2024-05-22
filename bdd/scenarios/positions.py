from datetime import datetime
from lib.trading.platform import TradingPlatform, SimulationPlatform, Candle
from pytest_bdd import scenarios, given, when, then, parsers
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

scenarios("../features/positions.feature")


@given("I start a new trading session")
def start_trading_session():
    global curr_time
    trading_platform.clear()
    curr_time = 0


@given(parsers.parse("I deposit {amount}$"))
def deposit(amount):
    trading_platform.deposit(int(amount))


@given(parsers.parse("I entered a {side} position of {quantity:d} {sym} stocks at {price:d}$ per share"))
@when(parsers.parse("I enter a {side} position of {quantity:d} {sym} stocks at {price:d}$ per share"))
def open_a_position(sym, side, quantity, price):
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
    position_is_open(side, sym)


@then("no positions should be open")
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


@when(parsers.parse("I close the {sym} position"))
def close_position(sym):
    pos = trading_platform.trading_session.get_current_position(sym)
    if pos.side == "long":
        trading_platform.submit_order(
            symbol=sym,
            quantity=pos.get_total_shares(),
            side="sell",
            flavor='market',
            date=get_curr_time())
    else:
        trading_platform.submit_order(
            symbol=sym,
            quantity=-pos.get_total_shares(),
            side="buy",
            flavor='market',
            date=get_curr_time())


@when(parsers.parse("I sell {quantity:d} {sym} stocks"))
def i_sell_stocks(quantity, sym):
    trading_platform.submit_order(
        symbol=sym,
        quantity=quantity,
        side="sell",
        flavor='market',
        date=get_curr_time())


@when(parsers.parse("I buy {quantity:d} {sym} stocks"))
def i_buy_stocks(quantity, sym):
    trading_platform.submit_order(
        symbol=sym,
        quantity=quantity,
        side="buy",
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


@then(parsers.parse("my equity should be {amount:d}$"))
def my_equity_should_be(amount):
    equity = trading_platform.get_current_equity()
    assert equity == amount


@then(parsers.parse("my equity should update to {value}$"))
def my_equity_should_be_updated(value):
    assert trading_platform.get_current_equity() == float(value)


@then(parsers.parse("the {symbol} position should report a profit of {profit:d}$"))
def the_position_should_report_a_profit(symbol, profit):
    position = trading_platform.trading_session.get_current_position(symbol)
    current_price = trading_platform.get_current_price_for(symbol)
    log.debug(f"average entry price: {position.get_average_entry_price()}")
    log.debug(f"average price      : {position.get_average_price()}")
    log.debug(f"open price         : {position.get_open_price()}")
    log.debug(f"total shares       : {position.get_total_shares()}")
    log.debug(f"profit             : {position.get_profit()}")
    log.debug(f"current profit     : {position.get_current_profit(current_price)}")
    assert position.get_current_profit(current_price) == profit

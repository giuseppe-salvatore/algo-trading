from lib.trading.platform import TradingPlatform, SimulationPlatform
from pytest_bdd import scenario, given, when, then, parsers

trading_platform: SimulationPlatform = TradingPlatform.get_trading_platform(
    "simulation"
)

received_error_message = False
current_cash = 0


@scenario("../features/cash-balance.feature", "Initial balance")
def test_initial_balance():
    pass


@scenario("../features/cash-balance.feature", "Deposit amount")
def test_deposit_amount():
    pass


@scenario(
    "../features/cash-balance.feature", "Withdraw amount smaller than cash balance"
)
def test_withdraw_less_than_cash_balance():
    pass


@scenario(
    "../features/cash-balance.feature", "Withdraw amount bigger than cash balance"
)
def test_withdraw_more_than_cash_balance():
    pass

@scenario(
    "../features/cash-balance.feature", "Reset trading platform"
)
def test_reset_trading_platform():
    pass


@given("I start trading AAPL stocks")
def start_trading():
    trading_platform.clear()


@when(parsers.parse("I deposit {amount}$"))
def deposit(amount):
    trading_platform.deposit(int(amount))


@when(parsers.parse("I withdraw {amount}$"))
def withdraw(amount):
    global received_error_message
    try:
        trading_platform.withdraw(int(amount))
    except Exception:
        received_error_message = True


@when("I reset the trading platform")
def reset_trading_platform():
    trading_platform.clear()


@then(parsers.parse("my cash balance should be {expected_amount}$"))
def check_balance(expected_amount):
    assert trading_platform.available_cash == int(expected_amount)


@then("I should receive an error message")
def check_error_message_received():
    global received_error_message
    assert received_error_message is True
    received_error_message = False


# @given("I submit a bracket market order to buy 10 AAPL stocks")
# def place_bracket_market_order():
#     global submitted_market_order_id
#     trading_platform.clear()
#     candle = Candle(datetime.now(), {
#         "high": 10,
#         "low": 10,
#         "open": 10,
#         "close": 10,
#         "volume": 5000,
#     })
#     trading_platform.tick("AAPL", candle)
#     submitted_market_order_id = trading_platform.submit_order(
#         symbol='AAPL',
#         quantity=10,
#         side='buy',
#         flavor='market',
#         date=datetime.now(),
#         take_profit_price=15,
#         stop_loss_price=8)

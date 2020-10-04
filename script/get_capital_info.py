from lib.trading.alpaca import AlpacaTrading

positions = None
proxy = AlpacaTrading()


def get_capital_invested(positions):
    capital = 0.0
    for pos in positions:
        capital += float(pos.market_value)
    print("You have currently invested " + "{:.2f}".format(capital) + "$")


def calculate_bracket_order_limits(positions):
    for pos in positions:
        symbol = pos.symbol
        value = float(pos.market_value)
        total_target = value * 1.02
        total_stop_loss = value * 0.99
        price_target = total_target / float(pos.qty)
        price_stop_loss = total_stop_loss / float(pos.qty)
        print(symbol + "(" + pos.qty + ")  ------------------------")
        print("  Target: {:.2f}".format(total_target))
        print("  Stop  : {:.2f}".format(total_stop_loss))
        print("  Price Target: {:.2f}".format(price_target))
        print("  Price Stop  : {:.2f}".format(price_stop_loss))
        print("")


if __name__ == "__main__":
    positions = proxy.get_positions()
    get_capital_invested(positions)
    calculate_bracket_order_limits(positions)

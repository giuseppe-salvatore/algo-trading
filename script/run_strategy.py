from lib.trading.alpaca import AlpacaTrading
from lib.strategies.macd.model import MovingAverageConvDiv

if __name__ == "__main__":

    api = AlpacaTrading()

    strategy = MovingAverageConvDiv()
    strategy.run_strategy(api)

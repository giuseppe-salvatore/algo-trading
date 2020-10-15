import argparse
import importlib
import pandas as pd
from lib.trading.alpaca import AlpacaTrading
from lib.strategies.base import BacktestStrategy
# from lib.strategies.rsi.model import RSIStrategy
# from lib.strategies.dummy import DummyStrategy
# from lib.strategies.macd.model import MovingAverageConvDiv
# from lib.strategies.ma_min_max.model import MovingAverageMinMax
# from strategies.macd_reversal.model import MovingAverageConvDivReversal


parser = argparse.ArgumentParser()
parser.add_argument("package")
parser.add_argument("module")
parser.add_argument("strategy_class")
args = parser.parse_args()


if __name__ == "__main__":

    pd.set_option('mode.chained_assignment', None)
    parallel_process = 4
    api = AlpacaTrading()
    backtester = BacktestStrategy()
    strategy = importlib.import_module('matplotlib.text')
    strategy_module = __import__(args.package + "." + args.module, fromlist=[args.strategy_class])
    strategy_class = getattr(strategy_module, args.strategy_class)
    backtester.run(api, strategy_class, parallel_process)

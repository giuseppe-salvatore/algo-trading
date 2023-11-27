import argparse
import importlib
import pandas as pd
from lib.util.logger import log

# from lib.trading.alpaca import AlpacaTrading
from lib.strategies.base import BacktestStrategy

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("module")
    parser.add_argument("strategy_class")
    args = parser.parse_args()

    pd.set_option("mode.chained_assignment", None)
    parallel_process = 4
    # api = AlpacaTrading()
    backtest = BacktestStrategy()
    strategy = importlib.import_module("matplotlib.text")
    strategy_module = __import__(
        args.package + "." + args.module, fromlist=[args.strategy_class]
    )
    strategy_class = getattr(strategy_module, args.strategy_class)
    log.debug("Selected {} strategy".format(strategy_class.get_name()))
    params = {
        "Strategy": strategy_class,
        "Parameter Size": "default",
        "Indicator List": ["rsi"],
        "Start Date": "2020-07-15",
        "End Date": "2020-09-30",
        "Trading Style": "multiday",
        "Market Data Provider": "Finnhub",
    }
    # backtester.run(api, strategy_class, parallel_process)
    # backtest.run_simulation(
    #     ["AAPL", "TSLA", "CSCO", "MSFT", "INTC", "SPCE", "NVDA", "AMD", "GM", "FCAU", "ZM", "JPM",
    #         "XOM", "QQQ", "SPY", "V", "WORK", "AXP", "MA", "LLY", "NDAQ", "MRNA", "GOOGL"],
    #     params,
    #     parallel_process
    # )
    backtest.run_simulation(["AAPL"], params, parallel_process)

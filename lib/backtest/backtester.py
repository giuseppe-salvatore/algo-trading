
import logging
import pandas as pd
from lib.util.logger import log
from lib.trading.alpaca import AlpacaTrading
from lib.strategies.base import BacktestStrategy
from lib.strategies.rsi.model import RSIStrategy
from lib.strategies.macd.model import MovingAverageConvDiv
from lib.strategies.ma_min_max.model import MovingAverageMinMax
#from strategies.macd_reversal.model import MovingAverageConvDivReversal


if __name__ == "__main__":
    
    pd.set_option('mode.chained_assignment', None)
    parallel_process = 1
    api = AlpacaTrading()
    backtester = BacktestStrategy()
    backtester.run(api, RSIStrategy, parallel_process)

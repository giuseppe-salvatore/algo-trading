
import logging
import pandas as pd
from api_proxy import TradeApiProxy
from strategies.model import BacktestStrategy
from strategies.rsi.model import RSIStrategy
from strategies.macd.model import MovingAverageConvDiv
from strategies.ma_min_max.model import MovingAverageMinMax
from strategies.macd_reversal.model import MovingAverageConvDivReversal


if __name__ == "__main__":
    
    pd.set_option('mode.chained_assignment', None)
    parallel_process = 2
    api = TradeApiProxy()
    backtester = BacktestStrategy()
    backtester.run(api, RSIStrategy, parallel_process)

import sys
import time
import datetime

import numpy as np
import pandas as pd
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from lib.trading.alpaca import AlpacaTrading



if __name__ == "__main__":

    api = AlpacaTrading()

    strategy = strategies.macd.model.MovingAverageConvDiv()
    strategy.run_strategy(api)
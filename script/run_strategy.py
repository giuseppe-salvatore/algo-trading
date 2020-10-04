import sys
import time
import datetime

import numpy as np
import pandas as pd
import finplot as fplt
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from api_proxy import TradeApiProxy

import strategies.scalping.run
import strategies.macd.model


if __name__ == "__main__":

    api = TradeApiProxy()

    strategy = strategies.macd.model.MovingAverageConvDiv()
    strategy.run_strategy(api)
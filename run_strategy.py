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


if __name__ == "__main__":

    api = TradeApiProxy()

    strategies.scalping.run.run_strategy(api)
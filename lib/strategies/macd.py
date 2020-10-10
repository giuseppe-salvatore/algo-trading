import sys
import time
import datetime
import traceback
import itertools

from lib.indicators.macd import MACD
from lib.trading.generic import Trade, Position
from lib.strategies.base import StockMarketStrategy
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

from lib.util.logger import log
# import lib.util.logger as logger
# logger.setup_logging("BaseStrategy")
# log = logger.logging.getLogger("BaseStrategy")

class MACDStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'dummy'
        self.long_name = "Dummy Strategy"

        self.result_folder = "strategies/" + self.name + "/backtesting/"
        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.profits = dict()
        self.current_positions = dict()

    def calculate_rsi(self, dataframe):
        return self.params.rsi_indicator.calculate(dataframe)

    def generate_strategy_signal(self, i):
        return

    def simulate(self, symbol):
        log.debug("Running simulation on " + symbol)

        data_provider = MarketDataProviderUtils.get_provider("Finnhub")
        data = data_provider.get_minute_candles(
            symbol,
            "2020-7-2",
            "2020-7-3",
            force_provider_fetch=False,
            store_fetched_data=True)

        macd_indicator = MACD()
        macd = macd_indicator.calculate(data)

        shares = 0
        prev_macd = None
        curr_macd = None
        position = None
        positions = []

        # Only trade during market hours but use the rest of the market data for
        # indicators
        filtered_data = data.between_time('15:30', '21:00')
        close_price = 0.0

        for idx, row in filtered_data.iterrows():

            curr_macd = macd.loc[idx, :]["histogram"]
            if prev_macd is None:
                prev_macd = curr_macd
                shares = round(2000 / row["open"])
                continue

            if prev_macd > 0 and curr_macd < 0:
                if position is None:
                    trade = Trade(symbol, shares, row["close"], "sell", idx)
                    position = Position(symbol, trade)
                    positions.append(position)
                else:
                    trade = Trade(symbol, shares, row["close"], "sell", idx)
                    if position.is_open():
                        position.update_position(trade)
                    else:
                        position = Position(symbol, trade)
                        positions.append(position)
            elif prev_macd < 0 and curr_macd > 0:
                if position is None:
                    trade = Trade(symbol, shares, row["close"], "buy", idx)
                    position = Position(symbol, trade)
                    positions.append(position)
                else:
                    trade = Trade(symbol, shares, row["close"], "buy", idx)
                    if position.is_open():
                        position.update_position(trade)
                    else:
                        position = Position(symbol, trade)
                        positions.append(position)
            else:
                pass

            close_price = row["close"]

            prev_macd = curr_macd

        positions[-1].liquidate(close_price)

        return positions

    def run_strategy(self):

        trades = {}

        try:
            for s in ["SPY"]:
                # for s in ["ABT", "AAPL",
                #           "BA", "BABA",
                #           "CSCO",
                #           "FB",
                #           "GOOGL", "GM",
                #           "INTC",
                #           "MRNA", "MSFT",
                #           "NIO", "NEE",
                #           "PYPL", "PTON",
                #           "QQQ",
                #           "ROKU",
                #           "SPY", "SNE",
                #           "TSLA", "TWTR",
                #           "XOM"]:
                # for s in ["AAPL"]:
                trades[s] = self.simulate(s)
        except Exception as e:
            log.error("Got exception " + str(e))
            traceback.print_tb(e.__traceback__)

        return trades

    def set_generated_param(self, params):
        return

    def generate_param_combination(self, size):

        params = []
        if size == 'small':
            long_mean_period = [22, 26, 30]
            short_mean_period = [10, 12, 14]
            mean_type = ["SMA"]
            source = ["close"]
        else:
            long_mean_period = [26]
            short_mean_period = [12]
            mean_type = ["SMA"]
            source = ["close"]

        param_product = itertools.product(
            long_mean_period,
            short_mean_period,
            mean_type,
            source
        )

        for param in param_product:
            params.append({
                'long_mean_period': param[0],
                'short_mean_period': param[1],
                'mean_type': param[2],
                'source': param[3]
            })

        return params

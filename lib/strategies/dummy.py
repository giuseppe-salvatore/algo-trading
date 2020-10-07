import time
import datetime
import traceback

from lib.trading.generic import Trade, Position
from lib.strategies.base import StockMarketStrategy

from lib.util.logger import log
# import lib.util.logger as logger
# logger.setup_logging("BaseStrategy")
# log = logger.logging.getLogger("BaseStrategy")

class DummyStrategy(StockMarketStrategy):

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

        if symbol == "AAPL":
            t1 = Trade(symbol, 10, 10.0, "buy", datetime.datetime(2020, 10, 10, 10, 10, 0))
            t2 = Trade(symbol, 15, 5.0, "buy", datetime.datetime(2020, 10, 10, 10, 20, 0))
            t3 = Trade(symbol, 25, 10.0, "sell", datetime.datetime(2020, 10, 10, 10, 30, 0))

            p = Position(symbol, t1)
            p.update_position(t2)
            p.update_position(t3)
            time.sleep(0.7)

            return [p]

        elif symbol == "BABA":
            t1 = Trade(symbol, 10, 110.0, "sell", datetime.datetime(2020, 10, 10, 11, 10, 0))
            t2 = Trade(symbol, 15, 50.0, "sell", datetime.datetime(2020, 10, 10, 11, 20, 0))
            t3 = Trade(symbol, 25, 70.0, "buy", datetime.datetime(2020, 10, 10, 11, 30, 0))

            p = Position(symbol, t1)
            p.update_position(t2)
            p.update_position(t3)
            time.sleep(1.2)

            return [p]
        else:
            t1 = Trade(symbol, 10, 125.0, "buy", datetime.datetime(2020, 10, 10, 12, 10, 0))
            t2 = Trade(symbol, 15, 100.0, "buy", datetime.datetime(2020, 10, 10, 12, 20, 0))
            t3 = Trade(symbol, 25, 120.0, "sell", datetime.datetime(2020, 10, 10, 12, 30, 0))
            time.sleep(1)

            p = Position(symbol, t1)
            p.update_position(t2)
            p.update_position(t3)

            return [p]



    def run_strategy(self, api):
        trades = {}

        try:
            for s in ["AAPL", "BABA", "TSLA"]:
                trades[s] = self.simulate(s)
        except Exception as e:
            log.error("Got exception " + str(e))
            traceback.print_tb(e.__traceback__)

        return trades

    def set_generated_param(self, params):
        return

    def generate_param_combination(self, size):
        params = [1, 2, 3, 4, 5, 6]
        return params

# import traceback
import itertools

from lib.indicators.moving_average import MovingAverage
from lib.trading.generic import Trade
from lib.strategies.base import StockMarketStrategy
from lib.market_data_provider.market_data_provider import MarketDataUtils
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

from lib.util.logger import log
# import lib.util.logger as logger
# logger.setup_logging("BaseStrategy")
# log = logger.logging.getLogger("BaseStrategy")

class MACrossoverStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'macd'
        self.long_name = "Moving Average Crossover"

        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.market_data = dict()

    @staticmethod
    def get_name():
        return 'macd'

    def calculate_rsi(self, dataframe):
        return self.params.rsi_indicator.calculate(dataframe)

    def generate_strategy_signal(self, i):
        return

    def get_moving_average_data(self, data, period, mean_type):
        ma = MovingAverage({
            "mean_period": period,
            "mean_type": mean_type,
            "source": "close"
        })
        return ma.calculate(data)

    def simulate(self,
                 symbol,
                 start_date,
                 end_date,
                 market_data_provider):
        log.debug("Running simulation on " + symbol)

        data_provider = MarketDataProviderUtils.get_provider(market_data_provider)
        data = data_provider.get_minute_candles(
            symbol,
            start_date,
            end_date,
            force_provider_fetch=False,
            store_fetched_data=True)
        self.market_data[symbol] = data

        # We need to calculate the fast and the slow moving averages to get the crossover
        slow_period = 50
        slow_mean = "SMA"
        fast_period = 20
        fast_mean = "SMA"
        fast_ma = self.get_moving_average_data(data, fast_period, fast_mean)
        slow_ma = self.get_moving_average_data(data, slow_period, slow_mean)
        data["crossover"] = (fast_ma["{} {}".format(fast_mean, fast_period)] -
                             slow_ma["{} {}".format(slow_mean, slow_period)])
        data["variance"] = data["close"].rolling(window=5).std()
        data["{} {}".format(fast_mean, fast_period)] = fast_ma
        data["{} {}".format(slow_mean, slow_period)] = slow_ma

        shares = 0
        prev_crossover = None
        curr_crossover = None

        # Only trade during market hours but use the rest of the market data for
        # indicators
        data["ohlc/4"] = (data["open"] + data["close"] + data["high"] + data["low"]) / 4
        market_open_time_str, market_close_time_str = MarketDataUtils.get_market_open_time(
            start_date)

        filtered_data = data.between_time(market_open_time_str, market_close_time_str)
        close_price = 0.0
        manage_trade = True
        buy_straight = False
        sell_straight = False

        for idx, row in filtered_data.iterrows():

            close_price = row["close"]
            curr_crossover = row['crossover']
            if prev_crossover is None:
                prev_crossover = curr_crossover
                shares = round(4000 / row["open"])
                continue

            curr_position = self.trade_session.get_current_position(symbol)
            # if idx == market_close_time_str:
            if idx.hour == 20 and idx.minute == 58:
                if curr_position is not None:
                    curr_profit = curr_position.get_current_profit(close_price)
                    log.info("Close at EOD rule: profit={:.2f}".format(
                        curr_profit
                    ))
                self.trade_session.liquidate(symbol, close_price, idx)
                prev_crossover = curr_crossover
                buy_straight = False
                sell_straight = False
                continue

            if buy_straight is True:
                self.trade_session.add_trade(Trade(symbol, shares, row["open"], "buy", idx))
                buy_straight = False
                prev_crossover = curr_crossover
                continue
            elif sell_straight is True:
                self.trade_session.add_trade(Trade(symbol, shares, row["open"], "sell", idx))
                sell_straight = False
                prev_crossover = curr_crossover
                continue

            if manage_trade and curr_position is not None:
                curr_profit = curr_position.get_current_profit(close_price)
                stop_loss = -40
                # if curr_profit > 0:
                #     stop_loss = max(stop_loss, curr_profit - 3)
                if curr_profit < stop_loss:
                    log.debug("Stop loss rule: profit={:.2f} stop_loss={:.2f}".format(
                        curr_profit,
                        stop_loss))
                    self.trade_session.liquidate(symbol, close_price, idx)
                    prev_crossover = curr_crossover
                    continue

            # ma200_val = ma_200.loc[idx]["SMA " + str(mean_period)]

            if prev_crossover > 0 and curr_crossover < 0:
                # if row["variance"] < 0.1:
                #     log.info("Low variance rule: {}".format(row["variance"]))
                #     prev_crossover = curr_crossover
                #     continue
                if curr_position is not None:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "sell", idx))
                    sell_straight = True
                else:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "sell", idx))
            elif prev_crossover < 0 and curr_crossover > 0:
                # if row["variance"] < 0.1:
                #     log.info("Low variance rule: {}".format(row["variance"]))
                #     prev_crossover = curr_crossover
                #     continue
                if curr_position is not None:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "buy", idx))
                    buy_straight = True
                else:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "buy", idx))

            prev_crossover = curr_crossover

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

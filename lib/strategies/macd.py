# import traceback
import itertools

from lib.indicators.macd import MACD
from lib.indicators.moving_average import MovingAverage
from lib.trading.generic import Trade
from lib.strategies.base import StockMarketStrategy
from lib.market_data_provider.market_data_provider import MarketDataUtils
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

from lib.util.logger import log
# import lib.util.logger as logger
# logger.setup_logging("BaseStrategy")
# log = logger.logging.getLogger("BaseStrategy")


class MACDStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'macd'
        self.long_name = "Moving Average Convergence Divergence"

        self.result_folder = "strategies/" + self.name + "/backtesting/"
        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.market_data = dict()
        self.platform = None

    @staticmethod
    def get_name():
        return 'macd'

    def calculate_rsi(self, dataframe):
        return self.params.rsi_indicator.calculate(dataframe)

    def generate_strategy_signal(self, i):
        return

    def simulate(self, symbol, start_date, end_date, market_data_provider):
        log.debug("Running simulation on " + symbol)

        data_provider = MarketDataProviderUtils.get_provider(
            market_data_provider)
        data = data_provider.get_minute_candles(symbol,
                                                start_date,
                                                end_date,
                                                force_provider_fetch=False,
                                                store_fetched_data=True)
        self.market_data[symbol] = data

        macd_indicator = MACD()
        mean_period = 120
        moving_average_indicator = MovingAverage({
            "mean_period": mean_period,
            "mean_type": "SMA",
            "source": "close"
        })
        macd = macd_indicator.calculate(data)
        ma_200 = moving_average_indicator.calculate(data)

        shares = 0
        prev_macd = None
        curr_macd = None

        # Only trade during market hours but use the rest of the market data for
        # indicators
        data["ohlc/4"] = (data["open"] + data["close"] + data["high"] +
                          data["low"]) / 4
        market_open_time_str, market_close_time_str = MarketDataUtils.get_market_open_time(
            start_date)

        filtered_data = data.between_time(market_open_time_str,
                                          market_close_time_str)
        close_price = 0.0
        manage_trade = True
        entry_filter = False

        for idx, row in filtered_data.iterrows():

            ohcl_4 = row["ohlc/4"]
            close_price = row["close"]
            curr_macd = macd.loc[idx, :]["histogram"]
            if prev_macd is None:
                prev_macd = curr_macd
                shares = round(2000 / row["open"])
                continue

            curr_position = self.trade_session.get_current_position(symbol)
            # if idx == market_close_time_str:
            if idx.hour == 20 and idx.minute == 58:
                if curr_position is not None:
                    curr_profit = curr_position.get_current_profit(close_price)
                    log.info(
                        "Close at EOD rule: profit={:.2f}".format(curr_profit))
                self.trade_session.liquidate(symbol, close_price, idx)
                continue

            if manage_trade and curr_position is not None:
                curr_profit = curr_position.get_current_profit(close_price)
                stop_loss = -10
                # if curr_profit > 0:
                #     stop_loss = max(stop_loss, curr_profit - 3)
                if curr_profit < stop_loss:
                    log.debug("Stop loss rule: profit={:.2f} stop_loss={:.2f}".
                              format(curr_profit, stop_loss))
                    self.trade_session.liquidate(symbol, close_price, idx)
                    prev_macd = curr_macd
                    continue

            ma200_val = ma_200.loc[idx]["SMA " + str(mean_period)]
            # log.debug("Position = {}, MA200 = {}, OHCL/4 = {}".format(
            #     curr_position is not None,
            #     ma200_val,
            #     ohcl_4
            # ))
            if prev_macd > 0 and curr_macd < 0:
                if curr_position is None and entry_filter is True:
                    if ma200_val is not None and close_price < ma200_val:
                        self.trade_session.add_trade(
                            Trade(symbol, shares, close_price, "sell", idx))
                    else:
                        log.debug(
                            "Above 200 SMA rule: oclh_4={:.2f} ma_200={:.2f}".
                            format(ohcl_4, ma200_val))
                else:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "sell", idx))
            elif prev_macd < 0 and curr_macd > 0:
                if curr_position is None and entry_filter is True:
                    if ma200_val is not None and close_price > ma200_val:
                        self.trade_session.add_trade(
                            Trade(symbol, shares, close_price, "buy", idx))
                    else:
                        log.debug(
                            "Below 200 SMA rule: oclh_4={:.2f} ma_200={:.2f}".
                            format(ohcl_4, ma200_val))
                else:
                    self.trade_session.add_trade(
                        Trade(symbol, shares, close_price, "buy", idx))

            prev_macd = curr_macd

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

        param_product = itertools.product(long_mean_period, short_mean_period,
                                          mean_type, source)

        for param in param_product:
            params.append({
                'long_mean_period': param[0],
                'short_mean_period': param[1],
                'mean_type': param[2],
                'source': param[3]
            })

        return params

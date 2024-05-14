import itertools
from lib.indicators.vwap import VWAP
from lib.trading.generic import Candle, Position
from lib.strategies.base import StockMarketStrategy
from lib.indicators.moving_average import MovingAverage
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
        # self.trade_session = self.platform.trading_session
        self.trade_session = None
        self.platform = None
        self.trading_style = None

    @staticmethod
    def get_name():
        return 'moving average crossover'

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

    def simulate(self, symbol, start_date, end_date, market_data_provider):

        initial_deposit = 100000
        self.platform.deposit(initial_deposit)
        log.debug(f"Initial deposit of {initial_deposit} as available cash")

        log.debug("Running simulation on " + symbol)

        data_provider = MarketDataProviderUtils.get_provider(
            market_data_provider)
        data = data_provider.get_minute_candles(symbol,
                                                start_date,
                                                end_date,
                                                force_provider_fetch=False,
                                                store_fetched_data=True)

        self.market_data[symbol] = data

        # We need to calculate the fast and the slow moving averages to get the crossover
        slow_period = 50
        slow_mean = "SMMA"
        fast_period = 20
        fast_mean = "SMMA"
        fast_ma = self.get_moving_average_data(data, fast_period, fast_mean)
        slow_ma = self.get_moving_average_data(data, slow_period, slow_mean)
        fast_ma_name = "{} {}".format(fast_mean, fast_period)
        data["speed"] = fast_ma[fast_ma_name].diff()
        data["crossover"] = (fast_ma[fast_ma_name] -
                             slow_ma["{} {}".format(slow_mean, slow_period)])
        data["variance"] = data["close"].rolling(window=5).std()
        data["{} {}".format(fast_mean, fast_period)] = fast_ma
        data["{} {}".format(slow_mean, slow_period)] = slow_ma

        mean_period = 120
        moving_average_indicator = MovingAverage({
            "mean_period": mean_period,
            "mean_type": "SMA",
            "source": "close"
        })
        ma_200 = moving_average_indicator.calculate(data)

        vwap_indicator = VWAP({"source": "close"})
        vwap = vwap_indicator.calculate(data)
        data["vwap"] = vwap.values
        print(data)

        shares = 0
        prev_crossover = None
        curr_crossover = None

        # Only trade during market hours but use the rest of the market data for
        # indicators
        data["ohlc/4"] = (data["open"] + data["close"] + data["high"] +
                          data["low"]) / 4
        market_open_time_str, market_close_time_str = MarketDataUtils.get_market_open_time(
            start_date)

        filtered_data = data.between_time("9:30", "15:59")
        close_price = 0.0
        manage_trade = True
        entry_filter = False
        stop_increase_threshold = 3
        curr_stop_increase_threshold = stop_increase_threshold
        take_profit_value = 1.5
        stop_loss_value = 0.5
        scaled = False

        dates = []
        equity = []
        entry = 0

        for idx, row in filtered_data.iterrows():

            dates.append(idx)
            close_price = row["close"]
            curr_speed = row["speed"]
            curr_crossover = row['crossover']
            if self.platform.tick(symbol, Candle(idx, row)):
                prev_crossover = curr_crossover
                continue

            if prev_crossover is None:
                prev_crossover = curr_crossover
                # shares = round(4000 / row["open"])
                shares = 10
                equity.append(float(0))
                continue

            curr_position: Position = self.trade_session.get_current_position(
                symbol)
            if idx.hour == 15 and idx.minute == 59:
                if self.trading_style is None or self.trading_style == 'intraday':
                    if curr_position is not None:
                        curr_profit = curr_position.get_current_profit(
                            close_price)
                        log.info("Close at EOD rule: profit={:.2f}".format(
                            curr_profit))
                        self.trade_session.liquidate(symbol, close_price, idx)
                        self.platform.cancel_order(
                            curr_position.get_leg('take_profit').id, idx)
                        self.platform.cancel_order(
                            curr_position.get_leg('stop_loss').id, idx)
                    prev_crossover = curr_crossover
                    equity.append(equity[-1])
                    continue

            # if buy_straight is True:
            #     self.trade_session.add_trade(Trade(symbol, shares, row["open"], "buy", idx))
            #     buy_straight = False
            #     prev_crossover = curr_crossover
            #     continue
            # elif sell_straight is True:
            #     self.trade_session.add_trade(Trade(symbol, shares, row["open"], "sell", idx))
            #     sell_straight = False
            #     prev_crossover = curr_crossover
            #     continue

            if manage_trade:
                if curr_position is not None:
                    curr_profit = curr_position.get_current_profit(close_price)
                    log.debug("Close {:.2f} Curr Profit: {:.2f}".format(
                        close_price, curr_profit))
                    if curr_profit >= curr_stop_increase_threshold and not scaled:
                        log.debug("Increasing threshold to {}".format(
                            curr_stop_increase_threshold))
                        # scaled = True
                        # time.sleep(1)
                        if curr_position.side == 'long':
                            prev_stop = curr_position.get_leg(
                                'stop_loss').stop_price
                            curr_position.get_leg(
                                'stop_loss').stop_price += 0.6
                            curr_stop = curr_position.get_leg(
                                'stop_loss').stop_price
                            log.debug(
                                "Updating stop ({:.2f}) -> ({:.2f})".format(
                                    prev_stop, curr_stop))
                            prev_profit = curr_position.get_leg(
                                'take_profit').limit_price
                            curr_position.get_leg(
                                'take_profit').limit_price += 0.15
                            curr_profit = curr_position.get_leg(
                                'take_profit').limit_price
                            log.debug(
                                "Updating profit ({:.2f}) -> ({:.2f})".format(
                                    prev_profit, curr_profit))
                        if curr_position.side == 'short':
                            prev_stop = curr_position.get_leg(
                                'stop_loss').stop_price
                            curr_position.get_leg(
                                'stop_loss').stop_price -= 0.6
                            curr_stop = curr_position.get_leg(
                                'stop_loss').stop_price
                            log.debug(
                                "Updating stop ({:.2f}) -> ({:.2f})".format(
                                    prev_stop, curr_stop))

                            prev_profit = curr_position.get_leg(
                                'take_profit').limit_price
                            curr_position.get_leg(
                                'take_profit').limit_price -= 0.15
                            curr_profit = curr_position.get_leg(
                                'take_profit').limit_price
                            log.debug(
                                "Updating profit ({:.2f}) -> ({:.2f})".format(
                                    prev_profit, curr_profit))
                        curr_stop_increase_threshold += stop_increase_threshold
                else:
                    curr_stop_increase_threshold = stop_increase_threshold
                    scaled = False

            ma200_val = ma_200.loc[idx]["SMA " + str(mean_period)]
            # log.debug("Position = {}, MA200 = {}, OHCL/4 = {}".format(
            #     curr_position is not None,
            #     ma200_val,
            #     close_price
            # ))

            if curr_position is None:
                # if prev_crossover < 0 and curr_crossover > 0:
                if curr_crossover > 0 and curr_speed > 0.05:
                    # if row["variance"] < 0.1:
                    #     log.info("Low variance rule: {}".format(row["variance"]))
                    #     prev_crossover = curr_crossover
                    #     continue

                    if entry_filter is True:
                        if ma200_val is not None and close_price > ma200_val:
                            self.platform.submit_order(
                                symbol=symbol,
                                quantity=shares,
                                side="buy",
                                date=idx,
                                flavor='market',
                                take_profit_price=(close_price +
                                                   take_profit_value),
                                stop_loss_price=(close_price -
                                                 stop_loss_value))
                    else:
                        self.platform.submit_order(
                            symbol=symbol,
                            quantity=shares,
                            side="buy",
                            date=idx,
                            flavor='market',
                            take_profit_price=(close_price +
                                               take_profit_value),
                            stop_loss_price=(close_price - stop_loss_value))
                # elif prev_crossover > 0 and curr_crossover < 0:
                elif curr_crossover < 0 and curr_speed < -0.05:
                    # if row["variance"] < 0.1:
                    #     log.info("Low variance rule: {}".format(row["variance"]))
                    #     prev_crossover = curr_crossover
                    #     continue

                    if entry_filter is True:
                        if ma200_val is not None and close_price < ma200_val:
                            self.platform.submit_order(
                                symbol=symbol,
                                quantity=shares,
                                side="sell",
                                date=idx,
                                flavor='market',
                                take_profit_price=close_price -
                                take_profit_value,
                                stop_loss_price=close_price + stop_loss_value)
                    else:
                        self.platform.submit_order(
                            symbol=symbol,
                            quantity=shares,
                            side="sell",
                            date=idx,
                            flavor='market',
                            take_profit_price=close_price - take_profit_value,
                            stop_loss_price=close_price + stop_loss_value)

            curr_position: Position = self.trade_session.get_current_position(
                symbol)

            if curr_position is not None:
                entry = curr_position.get_average_entry_price()
                if curr_position.side == 'long':
                    equity.append((close_price - entry) *
                                  curr_position.get_total_shares())
                else:
                    equity.append(-(close_price - entry) *
                                  curr_position.get_total_shares())
            else:
                equity.append(equity[-1])

            prev_crossover = curr_crossover

        log.debug("Stop feeding data on " + symbol)

        curr_pos = self.platform.trading_session.get_current_position(symbol)
        if curr_pos is not None and curr_pos.is_open():
            self.trade_session.liquidate(symbol, close_price, idx)

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

from lib.trading.generic import Candle
from lib.indicators.macd import MACD
from lib.indicators.moving_average import MovingAverage
from lib.strategies.base import StockMarketStrategy
from lib.market_data_provider.market_data_provider import MarketDataUtils
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

from lib.util.logger import log

class DummyStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'dummy'
        self.long_name = "Dummy Strategy"

        self.market_data = dict()
        # self.trade_session = self.platform.trading_session
        self.trade_session = None
        self.platform = None

    @staticmethod
    def get_name():
        return "DummyStrategy"

    def get_data(self, symbol, start_date, end_date, provider):
        data_provider = MarketDataProviderUtils.get_provider(provider)
        self.market_data[symbol] = data_provider.get_minute_candles(
            symbol,
            start_date,
            end_date,
            force_provider_fetch=False,
            store_fetched_data=False)

    def simulate(self, symbol, start_date, end_date, provider):

        log.debug("Start feeding data on " + symbol)

        self.get_data(symbol, start_date, end_date, provider)
        df = self.market_data[symbol]

        macd_indicator = MACD()
        macd = macd_indicator.calculate(df)

        mean_period = 120
        moving_average_indicator = MovingAverage({
            "mean_period": mean_period,
            "mean_type": "SMA",
            "source": "close"
        })
        ma_200 = moving_average_indicator.calculate(df)

        shares = 0
        prev_macd = None
        curr_macd = None

        df["ohlc/4"] = (df["open"] + df["close"] + df["high"] + df["low"]) / 4
        market_open_time_str, market_close_time_str = MarketDataUtils.get_market_open_time(
            start_date)

        filtered_data = df.between_time(market_open_time_str,
                                        market_close_time_str)
        close_price = 0.0
        entry_filter = True
        manage_trade = True
        stop_increase_threshold = 5

        counter = 0
        for idx, row in filtered_data.iterrows():

            if counter > 50000:
                log.debug(
                    "Reached the end ---------------------------------------------"
                )
                self.platform.print_all_orders()
                log.debug("Total trades = {}".format(
                    self.platform.trading_session.get_total_trades()))
                for pos in self.platform.trading_session.get_positions(symbol):
                    log.debug("{}".format(pos))
                break

            close_price = row["close"]
            self.platform.tick(symbol, Candle(idx, row))
            curr_macd = macd.loc[idx, :]["histogram"]
            if prev_macd is None:
                prev_macd = curr_macd
                shares = round(2000 / row["open"])
                continue

            curr_position = self.trade_session.get_current_position(symbol)
            if idx.hour == 20 and idx.minute == 58:
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
                    prev_macd = curr_macd
                    counter += 1
                    continue

            if manage_trade:
                if curr_position is not None:
                    curr_profit = curr_position.get_current_profit(close_price)
                    if curr_profit >= stop_increase_threshold:
                        log.debug("Increasing threshold to {}".format(
                            stop_increase_threshold))
                        # time.sleep(1)
                        if curr_position.side == 'buy':
                            curr_position.get_leg(
                                'stop_loss').stop_price += 0.5
                            curr_position.get_leg(
                                'take_profit').limit_price += 0.5
                        if curr_position.side == 'sell':
                            curr_position.get_leg(
                                'stop_loss').stop_price -= 0.5
                            curr_position.get_leg(
                                'take_profit').limit_price -= 0.5
                        stop_increase_threshold += 5
                else:
                    stop_increase_threshold = 5

            ma200_val = ma_200.loc[idx]["SMA " + str(mean_period)]
            log.debug("Position = {}, MA200 = {}, OHCL/4 = {}".format(
                curr_position is not None, ma200_val, close_price))

            if curr_position is None:
                if prev_macd < 0 and curr_macd > 0:
                    if entry_filter is True:
                        if ma200_val is not None and close_price > ma200_val:
                            self.platform.submit_order(
                                symbol=symbol,
                                quantity=shares,
                                side="buy",
                                date=idx,
                                flavor='market',
                                take_profit_price=close_price + 1.50,
                                stop_loss_price=close_price - 0.50)
                    else:
                        self.platform.submit_order(
                            symbol=symbol,
                            quantity=shares,
                            side="buy",
                            date=idx,
                            flavor='market',
                            take_profit_price=close_price + 1.50,
                            stop_loss_price=close_price - 0.50)
                elif prev_macd > 0 and curr_macd < 0:
                    if entry_filter is True:
                        if ma200_val is not None and close_price < ma200_val:
                            self.platform.submit_order(
                                symbol=symbol,
                                quantity=shares,
                                side="sell",
                                date=idx,
                                flavor='market',
                                take_profit_price=close_price - 1.5,
                                stop_loss_price=close_price + 0.50)
                    else:
                        self.platform.submit_order(
                            symbol=symbol,
                            quantity=shares,
                            side="sell",
                            date=idx,
                            flavor='market',
                            take_profit_price=close_price - 1.5,
                            stop_loss_price=close_price + 0.50)
            prev_macd = curr_macd
            counter += 1

        log.debug("Stop feeding data on " + symbol)

        curr_pos = self.platform.trading_session.get_current_position(symbol)
        if curr_pos is not None and curr_pos.is_open():
            self.trade_session.liquidate(symbol, close_price, idx)

        # For each row in dataframe
        # Create a candle object
        # if candle within maker hours
        # if candle within strategy trading hours
        # if last candle
        # cancel pending orders
        # if strategy is day trading
        # close pending positions
        # else
        # check if active candles have been triggered and generate trades to open/close positions
        # execute strategy actions
        # if in position
        # update bracket orders
        # submit orders

    def set_generated_param(self, params):
        return

    def generate_param_combination(self, size):
        params = [1, 2, 3, 4, 5, 6]
        return params

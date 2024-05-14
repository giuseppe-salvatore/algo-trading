import pandas._libs.tslibs.timestamps as ts

from datetime import timedelta
from lib.trading.generic import Candle
from lib.strategies.base import StockMarketStrategy
from lib.market_data_provider.market_data_provider import MarketDataUtils
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

from lib.util.logger import log
# import lib.util.logger as logger
# logger.setup_logging("BaseStrategy")
# log = logger.logging.getLogger("BaseStrategy")


class BuyAndHold(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'dummy'
        self.long_name = "Buy and Hold"

        self.market_data = dict()
        self.trade_session = None
        self.platform = None
        self.trading_style = None

    @staticmethod
    def get_name():
        return "Buy and Hold"

    def get_data(self, symbol, start_date, end_date, time_frame, provider):
        data_provider = MarketDataProviderUtils.get_provider(provider)
        # self.market_data[symbol] = data_provider.get_minute_candles(
        #     symbol,
        #     start_date,
        #     end_date,
        #     force_provider_fetch=False,
        #     store_fetched_data=False)
        self.market_data[symbol] = data_provider.get_candles(
            symbol,
            start_date,
            end_date,
            time_frame,
            force_provider_fetch=False,
            store_fetched_data=False)

        print(self.market_data[symbol])

        self.set_splits(data_provider.get_splits(symbol, start_date, end_date))

    def simulate(self, symbol, start_date, end_date, provider):

        initial_deposit = 100000

        self.platform.deposit(initial_deposit)
        log.debug(f"Initial deposit of {initial_deposit} as available cash")

        log.debug("Start feeding data on " + symbol)

        # First we get the market data in the range we are interested
        timeframe = {"multiplier": "30", "timeframe": "Min"}
        self.get_data(symbol, start_date, end_date, timeframe, "Finnhub")
        data = self.market_data[symbol]
        data["capital"] = 30000.0
        data["equity"] = 0.0
        data["shares"] = 0.0
        shares = None

        # Then we calculate all the moving averages here and all the other
        # indicators that need to be calculated on all the data
        # ...
        # ...

        # Now we get all the trading days
        dates = MarketDataUtils.get_market_days_in_range(start_date, end_date)

        # We get the exchange dataframe
        exchange_datetimes = MarketDataUtils.get_market_days_and_time_in_range(
            start_date, end_date)

        day_close_price = None
        close_price = 0.0
        shares = None

        idx_with_shares = []

        for trading_date in dates:
            # We extract the open/close market time
            open_time = MarketDataUtils.get_market_open_time_on_date(
                exchange_datetimes, trading_date).tz_localize(None)
            close_time: ts.Timestamp = MarketDataUtils.get_market_close_time_on_date(
                exchange_datetimes, trading_date).tz_localize(None)
            # We need to get the close time of the last candle that is at
            # 15:59 (usually). We can't use the close time of the 16:00 candle
            # because that would be at 16:00:59
            # close_candle =
            # close_time = close_time - timedelta(minutes=1)

            # These are only the rows of the specific trading date
            df_filtered_by_date = data.loc[str(trading_date), :]

            # We store the day open/close price
            day_close_price = data.loc[str(close_time - timedelta(
                minutes=int(timeframe["multiplier"]))), "close"]

            curr_position = self.platform.trading_session.get_current_position(
                symbol)
            self.apply_split(trading_date, curr_position)

            for idx, row in df_filtered_by_date.iterrows():

                close_price = row["close"]

                if shares is None:
                    shares = self.get_shares(20000, close_price)

                curr_position = self.platform.trading_session.get_current_position(
                    symbol)

                if open_time <= idx <= close_time:
                    self.platform.tick(symbol, Candle(idx, row))
                    if idx == open_time and curr_position is None:
                        if self.trading_style == 'multiday':
                            self.platform.submit_order(symbol=symbol,
                                                       quantity=shares,
                                                       side="buy",
                                                       date=idx,
                                                       flavor='market')
                            continue

                    if trading_date == dates[-1] and idx == close_time:
                        self.platform.trading_session.liquidate(
                            symbol, day_close_price, idx)
                        print("closing position")

                curr_position = self.platform.trading_session.get_current_position(
                    symbol)
                if curr_position is not None:
                    idx_with_shares.append(idx)

        log.debug("Stop feeding data on " + symbol)
        data.loc[idx_with_shares, "shares"] = shares

        # curr_pos = self.platform.trading_session.get_current_position(symbol)
        # if curr_pos is not None and curr_pos.is_open():

        #     data.loc[idx, "capital"] = capital_left + curr_equity
        #     capital_left = data.loc[idx, "capital"]
        #     data.loc[idx, "equity"] = 0

        # print(data.to_string())

        # For each row in dataframe
        # Create a candle object
        # if candle within maker hours
        # if candle within strategy trading hours
        # if last candle
        # cancel pending orders
        # if strategy is daytrading
        # close pending positions
        # else
        # check if active candles have been triggered and generate trades to open/close positions
        # execute strategy actions
        # if in position
        # update braket orders
        # submit orders

    def set_generated_param(self, params):
        return

    def generate_param_combination(self, size):
        params = [1, 2, 3, 4, 5, 6]
        return params

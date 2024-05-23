import itertools
from lib.indicators.vwap import VWAP
from lib.trading.generic import Candle, Position
from lib.strategies.base import StockMarketStrategy
from lib.indicators.moving_average import MovingAverage
from lib.market_data_provider.provider_utils import MarketDataProviderUtils
from lib.util.logger import log


class MACrossoverStrategy(StockMarketStrategy):

    def __init__(self):
        super().__init__()
        self.params = None
        self.name = 'macd'
        self.long_name = "Moving Average Crossover"
        self.start_capital = 25000.0
        self.current_capital = self.start_capital
        self.market_data = {}
        self.trade_session = None
        self.platform = None
        self.trading_style = None

    @staticmethod
    def get_name() -> str:
        return 'moving average crossover'

    def calculate_rsi(self, dataframe):
        return self.params.rsi_indicator.calculate(dataframe)

    def get_moving_average_data(self, data, period, mean_type):
        ma = MovingAverage({
            "mean_period": period,
            "mean_type": mean_type,
            "source": "close"
        })
        return ma.calculate(data)

    def simulate(self, symbol: str, start_date: str, end_date: str, market_data_provider: str):
        initial_deposit = 500000000
        self.platform.deposit(initial_deposit)
        log.debug(f"Initial deposit of {initial_deposit} as available cash")

        log.debug(f"Running simulation on {symbol}")

        data_provider = MarketDataProviderUtils.get_provider(market_data_provider)
        data = data_provider.get_minute_candles(
            symbol, start_date, end_date, force_provider_fetch=False, store_fetched_data=True)
        self.market_data[symbol] = data

        slow_period, fast_period = 50, 20
        slow_mean, fast_mean = "SMMA", "SMMA"
        fast_ma = self.get_moving_average_data(data, fast_period, fast_mean)
        slow_ma = self.get_moving_average_data(data, slow_period, slow_mean)
        fast_ma_name, slow_ma_name = f"{fast_mean} {fast_period}", f"{slow_mean} {slow_period}"

        data["speed"] = fast_ma[fast_ma_name].diff()
        data["crossover"] = fast_ma[fast_ma_name] - slow_ma[slow_ma_name]
        data["variance"] = data["close"].rolling(window=5).std()
        data[fast_ma_name] = fast_ma
        data[slow_ma_name] = slow_ma

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

        shares = 10
        prev_crossover, curr_crossover = None, None

        data["ohlc/4"] = (data["open"] + data["close"] + data["high"] + data["low"]) / 4
        filtered_data = data.between_time("9:30", "15:59")
        close_price, entry, curr_stop_increase_threshold = 0.0, 0, 3
        take_profit_value, stop_loss_value = 1.5, 0.5
        scaled, manage_trade, entry_filter = False, True, False

        dates, equity = [], []

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
                equity.append(float(0))
                continue

            curr_position: Position = self.trade_session.get_current_position(symbol)
            if idx.hour == 15 and idx.minute == 59:
                if self.trading_style is None or self.trading_style == 'intraday':
                    if curr_position:
                        self._close_position_at_eod(curr_position, close_price, idx)
                    prev_crossover = curr_crossover
                    equity.append(equity[-1])
                    continue

            if manage_trade and curr_position:
                self._manage_existing_trade(curr_position, close_price, curr_stop_increase_threshold, scaled)

            ma200_val = ma_200.loc[idx]["SMA " + str(mean_period)]

            if not curr_position:
                self._attempt_new_entry(symbol, idx, close_price, curr_crossover, curr_speed,
                                        entry_filter, ma200_val, shares, take_profit_value, stop_loss_value)

            curr_position = self.trade_session.get_current_position(symbol)

            if curr_position:
                entry = curr_position.get_average_entry_price()
                equity.append(self._calculate_equity(close_price, entry, curr_position))
            else:
                equity.append(equity[-1])

            prev_crossover = curr_crossover

        log.debug(f"Stop feeding data on {symbol}")

        self._finalize_open_position(symbol, close_price, idx)

    def _close_position_at_eod(self, curr_position, close_price, idx):
        curr_profit = curr_position.get_current_profit(close_price)
        log.info(f"Close at EOD rule: profit={curr_profit:.2f}")
        self.trade_session.liquidate(curr_position.symbol, close_price, idx)
        self.platform.cancel_order(curr_position.get_leg('take_profit').id, idx)
        self.platform.cancel_order(curr_position.get_leg('stop_loss').id, idx)

    def _manage_existing_trade(self, curr_position, close_price, curr_stop_increase_threshold, scaled):
        curr_profit = curr_position.get_current_profit(close_price)
        log.debug(f"Close {close_price:.2f} Curr Profit: {curr_profit:.2f}")
        stop_increase_threshold = 3
        if curr_profit >= curr_stop_increase_threshold and not scaled:
            log.debug(f"Increasing threshold to {curr_stop_increase_threshold}")
            self._update_stop_and_profit(curr_position)
            curr_stop_increase_threshold += stop_increase_threshold

    def _update_stop_and_profit(self, curr_position):
        if curr_position.side == 'long':
            self._update_long_position(curr_position)
        elif curr_position.side == 'short':
            self._update_short_position(curr_position)

    def _update_long_position(self, curr_position):
        prev_stop = curr_position.get_leg('stop_loss').stop_price
        curr_position.get_leg('stop_loss').stop_price += 0.6
        curr_stop = curr_position.get_leg('stop_loss').stop_price
        log.debug(f"Updating stop ({prev_stop:.2f}) -> ({curr_stop:.2f})")

        prev_profit = curr_position.get_leg('take_profit').limit_price
        curr_position.get_leg('take_profit').limit_price += 0.15
        curr_profit = curr_position.get_leg('take_profit').limit_price
        log.debug(f"Updating profit ({prev_profit:.2f}) -> ({curr_profit:.2f})")

    def _update_short_position(self, curr_position):
        prev_stop = curr_position.get_leg('stop_loss').stop_price
        curr_position.get_leg('stop_loss').stop_price -= 0.6
        curr_stop = curr_position.get_leg('stop_loss').stop_price
        log.debug(f"Updating stop ({prev_stop:.2f}) -> ({curr_stop:.2f})")

        prev_profit = curr_position.get_leg('take_profit').limit_price
        curr_position.get_leg('take_profit').limit_price -= 0.15
        curr_profit = curr_position.get_leg('take_profit').limit_price
        log.debug(f"Updating profit ({prev_profit:.2f}) -> ({curr_profit:.2f})")

    def _attempt_new_entry(
        self,
        symbol,
        idx,
        close_price,
        curr_crossover,
        curr_speed,
        entry_filter,
        ma200_val,
        shares,
        take_profit_value,
        stop_loss_value
    ):
        if (curr_crossover > 0 and curr_speed > 0.05):
            if entry_filter and ma200_val is not None and close_price > ma200_val:
                self._submit_order(symbol, idx, "buy", shares, close_price, take_profit_value, stop_loss_value)
            elif not entry_filter:
                self._submit_order(symbol, idx, "buy", shares, close_price, take_profit_value, stop_loss_value)
        elif (curr_crossover < 0 and curr_speed < -0.05):
            if entry_filter and ma200_val is not None and close_price < ma200_val:
                self._submit_order(symbol, idx, "sell", shares, close_price, take_profit_value, stop_loss_value)
            elif not entry_filter:
                self._submit_order(symbol, idx, "sell", shares, close_price, take_profit_value, stop_loss_value)

    def _submit_order(self, symbol, idx, side, shares, close_price, take_profit_value, stop_loss_value):
        self.platform.submit_order(
            symbol=symbol,
            quantity=shares,
            side=side,
            date=idx,
            flavor='market',
            take_profit_price=(close_price + take_profit_value if side == "buy" else close_price - take_profit_value),
            stop_loss_price=(close_price - stop_loss_value if side == "buy" else close_price + stop_loss_value)
        )

    def _calculate_equity(self, close_price, entry, curr_position):
        if curr_position.side == 'long':
            return (close_price - entry) * curr_position.get_total_shares()
        else:
            return -(close_price - entry) * curr_position.get_total_shares()

    def _finalize_open_position(self, symbol, close_price, idx):
        curr_pos = self.platform.trading_session.get_current_position(symbol)
        if curr_pos and curr_pos.is_open():
            self.trade_session.liquidate(symbol, close_price, idx)

    def set_generated_param(self, params):
        self.params = params

    def generate_param_combination(self, size: str):
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

        param_product = itertools.product(long_mean_period, short_mean_period, mean_type, source)

        for param in param_product:
            params.append({
                'long_mean_period': param[0],
                'short_mean_period': param[1],
                'mean_type': param[2],
                'source': param[3]
            })

        return params

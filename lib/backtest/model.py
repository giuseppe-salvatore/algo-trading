import os
import traceback
from datetime import datetime
from lib.util.logger import log
from lib.trading.generic import TradeSession
from lib.trading.platform import TradingPlatform
from lib.market_data_provider.provider_utils import MarketDataProviderUtils
# from lib.market_data_provider.market_data_provider import MarketDataUtils


class BacktestParams():

    @staticmethod
    def get_param_size():
        return ["default", "light", "small", "medium", "full"]

    @staticmethod
    def get_available_indicators():
        return ["rsi", "macd", "ma", "bb"]

    @staticmethod
    def get_trading_style():
        return ["intraday", "multiday"]

    @staticmethod
    def check_param_key(key, params, msg, success):
        if key not in params:
            success = False
            msg += "Missing required param {}\n".format(key)
        return success, msg

    @staticmethod
    def check_date(param_key, param_value, msg, success):
        if type(param_value) is not datetime:
            if type(param_value) is str:
                try:
                    datetime.strptime(param_value, "%Y-%m-%d")
                except Exception:
                    success = False
                    msg += "{} has to be datetime or a string of format {}".format(
                        param_key, "%Y-%m-%d\n")
            else:
                success = False
                msg += "{} has to be datetime or a string of format {}".format(
                    param_key, "%Y-%m-%d\n")
        return success, msg

    @staticmethod
    def validate_param_set(params):

        msg = ""
        success = True

        success, msg = BacktestParams.check_param_key("Strategy", params, msg,
                                                      success)
        success, msg = BacktestParams.check_param_key("Parameter Size", params,
                                                      msg, success)
        success, msg = BacktestParams.check_param_key("Indicator List", params,
                                                      msg, success)
        success, msg = BacktestParams.check_param_key("Start Date", params,
                                                      msg, success)
        success, msg = BacktestParams.check_param_key("End Date", params, msg,
                                                      success)
        success, msg = BacktestParams.check_param_key("Trading Style", params,
                                                      msg, success)
        success, msg = BacktestParams.check_param_key("Market Data Provider",
                                                      params, msg, success)

        if not success:
            raise ValueError(msg)

        # Verifying the parameter size
        param = "Parameter Size"
        if params[param] not in BacktestParams.get_param_size():
            success = False
            msg += "{} can only be {} but {} provided instead".format(
                param, BacktestParams.get_param_size(), params[param])

        # Verifying the indicator's list
        param = "Indicator List"
        if type(params[param]) is not list:
            success = False
            msg += "{} has to be a list of known indicators".format(param)
        for elem in params[param]:
            if elem not in BacktestParams.get_available_indicators():
                success = False
                msg += "{} can only be {} but {} provided instead".format(
                    param, BacktestParams.get_available_indicators(),
                    params[param])

        # Verifying the start date and end date
        param_key = "Start Date"
        success, msg = BacktestParams.check_date(param_key, params[param_key],
                                                 msg, success)
        param_key = "End Date"
        success, msg = BacktestParams.check_date(param_key, params[param_key],
                                                 msg, success)

        # Verifying the trading style
        param = "Trading Style"
        if params[param] not in BacktestParams.get_trading_style():
            success = False
            msg += "{} can only be {} but {} provided instead".format(
                param, BacktestParams.get_trading_style(), params[param])

        # Verifying the trading style
        param = "Trading Style"
        if params[param] not in BacktestParams.get_trading_style():
            success = False
            msg += "{} can only be {} but {} provided instead".format(
                param, BacktestParams.get_trading_style(), params[param])

        # Verifying the market data provider
        param = "Market Data Provider"
        if params[
                param] not in MarketDataProviderUtils.get_available_providers(
                ):
            success = False
            msg += "{} can only be {} but {} provided instead".format(
                param, MarketDataProviderUtils.get_available_providers(),
                params[param])

        if not success:
            raise ValueError(msg)


class BacktestResult():

    def __init__(self):
        self._total_profit = None
        self._trading_session = TradeSession()
        self._success_ratio = None
        self._total_trades = None
        self._market_data = {}

    @property
    def total_profit(self):
        if self.positions is None:
            log.warning("No positions available")
            return 0
        total_profit = 0.0
        for pos in self.positions:
            total_profit += 0
        return self.positions.get_profit()

    @total_profit.setter
    def total_profit(self, val):
        self._total_profit = val

    @property
    def trading_session(self):
        return self._trading_session

    @trading_session.setter
    def trading_session(self, val):
        self._trading_session = val

    @property
    def success_ratio(self):
        return self._success_ratio

    @success_ratio.setter
    def success_ratio(self, val):
        self._success_ratio = val

    @property
    def total_trades(self):
        return self._total_trades

    @total_trades.setter
    def total_trades(self, val):
        self._total_trades = val

    @property
    def market_data(self):
        return self._market_data

    @market_data.setter
    def market_data(self, val):
        self._market_data = val


class BacktestSimulation():

    def __init__(self):
        self._symbols = None
        self._strategy_class = None
        self._start_date = None
        self._end_date = None
        self._indicator_list = None
        self._trading_style = None
        self._trading_mgt_class = None
        self._market_data_provider = None
        self._trading_session = TradeSession()
        self._results = BacktestResult()
        self._result_folder = None
        self._platform = TradingPlatform.get_trading_platform("simulation")

    def execute(self):

        # start_date = MarketDataUtils.from_string_to_datetime(self.start_date)
        # end_date = MarketDataUtils.from_string_to_datetime(self.end_date)
        # market_dates = MarketDataUtils.get_market_days_in_range(start_date, end_date)

        self._results = BacktestResult()

        if self.symbols is None or len(self.symbols) == 0:
            return self

        for symbol in self.symbols:
            try:
                log.info(
                    "Start executing of {} simulation for symbol {}".format(
                        self.strategy_class.get_name(), symbol))
                strategy = self.strategy_class()
                strategy.trade_session = self._results.trading_session
                strategy.platform = self._platform
                strategy.platform.trading_session = strategy.trade_session
                strategy.trading_style = self._trading_style
                strategy.simulate(symbol, self.start_date, self.end_date,
                                  self.market_data_provider)
                log.info("Completed executing of {} simulation for symbol {}".
                         format(self.strategy_class.get_name(), symbol))
                self._results.market_data[symbol] = strategy.market_data
                self._results.trading_session = strategy.trade_session
            except Exception as e:
                log.critical(str(e))
                log.critical("Running simulation for {}".format(symbol))
                traceback.print_tb(e.__traceback__)

        return self

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, val):
        self._symbols = val

    @property
    def strategy_class(self):
        return self._strategy_class

    @strategy_class.setter
    def strategy_class(self, val):
        self._strategy_class = val

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, val):
        self._start_date = val

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, val):
        self._end_date = val

    @property
    def trading_style(self):
        return self._trading_style

    @trading_style.setter
    def trading_style(self, val):
        self._trading_style = val

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, val):
        self._results = val

    @property
    def market_data_provider(self):
        return self._market_data_provider

    @market_data_provider.setter
    def market_data_provider(self, val):
        self._market_data_provider = val

    @property
    def indicator_list(self):
        return self._indicator_list

    @indicator_list.setter
    def indicator_list(self, val):
        self._indicator_list = val

    @property
    def result_folder(self):
        if self._result_folder is None:
            date = datetime.now()
            self._result_folder = "data/simulations/" + date.strftime(
                "%Y-%m-%d_%h-%M-%s")
            os.makedirs(self._result_folder)

        return self._result_folder

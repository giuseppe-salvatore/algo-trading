import unittest
import importlib
from datetime import datetime
# Project specific imports
from lib.util.logger import log
from lib.backtest.runner import BacktestStrategy
from lib.backtest.model import BacktestParams
from lib.strategies.dummy import DummyStrategy


class StrategyBacktestParametersTest(unittest.TestCase):

    def test_param_size_has_default(self):

        param_sizes = BacktestParams.get_param_size()
        self.assertTrue("default" in param_sizes)

    def test_param_size_has_light(self):

        param_sizes = BacktestParams.get_param_size()
        self.assertTrue("light" in param_sizes)

    def test_param_size_has_small(self):

        param_sizes = BacktestParams.get_param_size()
        self.assertTrue("small" in param_sizes)

    def test_param_size_has_medium(self):

        param_sizes = BacktestParams.get_param_size()
        self.assertTrue("medium" in param_sizes)

    def test_param_size_has_full(self):

        param_sizes = BacktestParams.get_param_size()
        self.assertTrue("full" in param_sizes)

    def test_param_size_has_not_unexpected(self):

        expected_param_sizes = ["default", "light", "small", "medium", "full"]
        param_sizes = BacktestParams.get_param_size()
        success = True
        for elem in param_sizes:
            if elem not in expected_param_sizes:
                log.error("Unexpected param_size: " + elem)
                success = False
        self.assertTrue(success)

    def test_trading_style_has_intraday(self):

        trading_style = BacktestParams.get_trading_style()
        self.assertTrue("intraday" in trading_style)

    def test_trading_style_has_multyday(self):

        trading_style = BacktestParams.get_trading_style()
        self.assertTrue("multiday" in trading_style)

    def test_trading_style_has_not_unexpected(self):

        expected_trading_styles = ["multiday", "intraday"]
        trading_style = BacktestParams.get_trading_style()
        success = True
        for elem in trading_style:
            if elem not in expected_trading_styles:
                log.error("Unexpected trading_style: " + elem)
                success = False
        self.assertTrue(success)

    def test_validate_good_parameters_success(self):
        BacktestParams.validate_param_set({
            "Strategy": "a strategy",
            "Parameter Size": "small",
            "Indicator List": ["rsi"],
            "Start Date": datetime.now(),
            "End Date": datetime.now(),
            "Trading Style": "intraday",
            "Market Data Provider": "Polygon"
        })

    def test_validate_good_parameters_date_string_success(self):
        BacktestParams.validate_param_set({
            "Strategy": "a strategy",
            "Parameter Size": "small",
            "Indicator List": ["rsi"],
            "Start Date": "2020-10-09",
            "End Date": "2020-10-19",
            "Trading Style": "intraday",
            "Market Data Provider": "Polygon"
        })

    def test_validate_parameters_missing_strategy_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Parameter Size": "small",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_missing_parameter_size_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_missing_indicator_list_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_missing_start_date_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": ["rsi"],
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_missing_end_date_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_missing_trading_style_key_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now()
                          })

    def test_validate_parameters_non_existing_param_size_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "non existing value",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_non_existing_indicator_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": ["non existing indicator"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_non_existing_trading_style_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": ["rsi"],
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "non existing"
                          })

    def test_validate_parameters_wrong_inidicator_type_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": "rsi",
                              "Start Date": datetime.now(),
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_wrong_start_date_type_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": "rsi",
                              "Start Date": [],
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_wrong_end_date_type_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": "rsi",
                              "Start Date": datetime.now(),
                              "End Date": [],
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_wrong_start_date_format_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": "rsi",
                              "Start Date": "2020-05-111",
                              "End Date": datetime.now(),
                              "Trading Style": "intraday"
                          })

    def test_validate_parameters_wrong_end_date_format_fail(self):
        self.assertRaises(ValueError,
                          BacktestParams.validate_param_set,
                          {
                              "Strategy": "a strategy",
                              "Parameter Size": "small",
                              "Indicator List": "rsi",
                              "Start Date": datetime.now(),
                              "End Date": "2020-05-111",
                              "Trading Style": "intraday"
                          })


class DummyStrategyScenarios(unittest.TestCase):

    def test_dummy_started_from_backtester(self):
        parallel_process = 4
        # api = AlpacaTrading()
        backtest = BacktestStrategy()
        # strategy = importlib.import_module('matplotlib.text')
        strategy_module = __import__("lib.strategies.dummy", fromlist=["DummyStrategy"])
        strategy_class = getattr(strategy_module, "DummyStrategy")
        log.debug("Selected {} strategy".format(strategy_class.get_name()))
        params = {
            "Strategy": strategy_class,
            "Parameter Size": "default",
            "Indicator List": ["rsi"],
            "Start Date": "2020-10-12",
            "End Date": "2020-10-14",
            "Trading Style": "intraday",
            "Market Data Provider": "Finnhub",
            "Draw Charts": False
        }
        backtest.run_simulation(
            ["AAPL", ],
            params,
            parallel_process
        )

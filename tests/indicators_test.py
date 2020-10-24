import unittest
from datetime import datetime

# Project specific imports from lib
from lib.util.logger import log
from lib.indicators.rsi import RelativeStrenghtIndex
from lib.indicators.macd import MACD
from lib.indicators.moving_average import MovingAverage


class MovingAverageTest(unittest.TestCase):

    def test_default_parameters_keys_set(self):
        ma = MovingAverage()
        self.assertTrue("source" in ma.params)
        self.assertTrue("mean_type" in ma.params)
        self.assertTrue("mean_period" in ma.params)

    def test_default_parameters_values_set(self):
        ma = MovingAverage()
        self.assertEqual(ma.params["source"], "close")
        self.assertEqual(ma.params["mean_type"], "SMA")
        self.assertEqual(ma.params["mean_period"], 200)

    def test_default_name(self):
        ma = MovingAverage()
        self.assertEqual(ma.name, "SMA 200 close")

    def test_name_update(self):
        ma = MovingAverage()
        ma.set_params({
            "mean_period": 100,
            "mean_type": "EMA",
            "source": "hl"
        })
        self.assertEqual(ma.name, "EMA 100 hl")

    def test_name_init(self):
        ma = MovingAverage({
            "mean_period": 100,
            "mean_type": "EMA",
            "source": "hl"
        })
        self.assertEqual(ma.name, "EMA 100 hl")

class RelativeStrenghtIndexTest(unittest.TestCase):

    def test_default_parameters_keys_set(self):
        rsi = RelativeStrenghtIndex()
        self.assertTrue("source" in rsi.params)
        self.assertTrue("mean_type" in rsi.params)
        self.assertTrue("mean_period" in rsi.params)
        self.assertTrue("period" in rsi.params)

    def test_default_parameters_values_set(self):
        rsi = RelativeStrenghtIndex()
        self.assertEqual(rsi.params["source"], "close")
        self.assertEqual(rsi.params["mean_type"], "SMA")
        self.assertEqual(rsi.params["mean_period"], 4)
        self.assertEqual(rsi.params["period"], 14)

    def test_default_name(self):
        rsi = RelativeStrenghtIndex()
        self.assertEqual(rsi.name, "RSI 14 close")

    def test_name_update(self):
        rsi = RelativeStrenghtIndex()
        rsi.set_params({
            "period": 20,
            "mean_period": 4,
            "mean_type": "EMA",
            "source": "hcl"
        })
        self.assertEqual(rsi.name, "RSI 20 hcl")

    def test_name_init(self):
        rsi = RelativeStrenghtIndex({
            "period": 20,
            "mean_period": 4,
            "mean_type": "EMA",
            "source": "hcl"
        })
        self.assertEqual(rsi.name, "RSI 20 hcl")

class MACDTest(unittest.TestCase):

    def test_default_parameters_keys_set(self):
        macd = MACD()
        self.assertTrue("source" in macd.params)
        self.assertTrue("mean_type" in macd.params)
        self.assertTrue("long_mean_period" in macd.params)
        self.assertTrue("short_mean_period" in macd.params)
        self.assertTrue("signal_smooth" in macd.params)

    # def test_default_parameters_values_set(self):
    #     macd = MACD()
    #     self.assertEqual(macd.params["source"], "close")
    #     self.assertEqual(macd.params["mean_type"], "SMA")
    #     self.assertEqual(macd.params["mean_period"], 200)

    # def test_default_name(self):
    #     macd = MACD()
    #     self.assertEqual(macd.name, "SMA 200 close")

    # def test_name_update(self):
    #     macd = MACD()
    #     macd.set_params({
    #         "mean_period": 100,
    #         "mean_type": "EMA",
    #         "source": "hl"
    #     })
    #     self.assertEqual(macd.name, "EMA 100 hl")

    # def test_name_init(self):
    #     macd = MACD({
    #         "mean_period": 100,
    #         "mean_type": "EMA",
    #         "source": "hl"
    #     })
    #     self.assertEqual(macd.name, "EMA 100 hl")

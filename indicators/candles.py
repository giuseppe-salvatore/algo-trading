

BULL_BEAR_PERC = 3.0

class CandleStick():
    def __init__(self,ohlc_array):
        self.ohlc = ohlc_array
        self.open = self.ohlc[0]
        self.high = self.ohlc[1]
        self.low = self.ohlc[2]
        self.close = self.ohlc[3]
        self.ohlc_dic = { 
            "open": self.ohlc[0],
            "high": self.ohlc[1],
            "low": self.ohlc[2],
            "close": self.ohlc[3]
        }
        

    def is_green(self):
        if self.open > self.close:
            return True
        return False
        
    def is_red(self):
        if self.close > self.open:
            return True
        return False

    def is_long(self):
        pass

    def is_short(self):
        pass

    def is_medium(self):
        pass

    def is_bullish(self):
        if self.is_long() and self.is_green():
            # We calculate the threshold 
            hundred = self.high - self.low
            threshold = hundred * BULL_BEAR_PERC * 100.0

            # If the close price is within BULL_BEAR_PERC
            # from high than we say this is a bullish
            if self.close > self.high - threshold:
                return True
            return False
        return False

    def is_bearhish(self):
        if self.is_long() and self.is_red():
            # We calculate the threshold 
            hundred = self.high - self.low
            threshold = hundred * BULL_BEAR_PERC * 100.0

            # If the close price is within BULL_BEAR_PERC
            # from high than we say this is a bullish
            if self.close > self.low + threshold:
                return True
            return False
        return False

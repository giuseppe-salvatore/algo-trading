import logging
import pandas as pd

logging.basicConfig(level='WARNING')
log = logging.getLogger(__name__)
log.setLevel('DEBUG')

class RSIIndicator():

    def __init__(self, period, mean_period, mean_type,  source):
        self.period = period
        # We need some sort of mean to avoid RSI going crazily up and down
        self.mean_period = mean_period
        self.mean_type = mean_type
        self.source = source
        
    
    def calculate(self, data):

        source = data[self.source]
        delta = source.diff()
        up = delta.copy().rolling(window=self.mean_period).mean()
        down = delta.copy().rolling(window=self.mean_period).mean()
        up[up < 0] = 0
        down[down > 0] = 0

        roll_up = None
        roll_down = None
        # Calculate the RSI based on EWMA
        if self.mean_type == 'EMA':
            roll_up = up.ewm(span=self.period).mean()
            roll_down = down.abs().ewm(span=self.period).mean()
            
        # Calculate the RSI based on SMA
        elif self.mean_type == 'SMA':
            # Calculate the SMA
            roll_up = up.rolling(self.period).mean()
            roll_down = down.abs().rolling(self.period).mean()
        
        else:
            raise Exception("Mean type parameter can only be EMA or SMA")
            
        rs = roll_up / roll_down
        rsi = 100.0 - (100.0 / (1.0 + rs))

        return rsi
import logging
import numpy as np 
import pandas as pd


logging.basicConfig(level='WARNING')
log = logging.getLogger(__name__)
log.setLevel('DEBUG')


class BollingerBands():

    def __init__(self, params):
        self.median_period = int(params['median_period'])
        self.stdev_factor = float(params['stdev_factor'])
        self.source = params['source']
        self.bands_dataframe = None

    def calculate(self, data):
        
        data['mean'] = data[self.source].rolling(window=self.median_period).mean()
        data['upper band'] = data['mean'] + self.stdev_factor * data[self.source].rolling(window=self.median_period).std()
        data['lower band'] = data['mean'] - self.stdev_factor * data[self.source].rolling(window=self.median_period).std()
        data['band diff'] = data['upper band'] - data['lower band']
        diffs = data['band diff'].diff()
        data.assign(
            change=np.where(
                diffs > 0, 1, np.where(
                diffs < 0, -1, 0)
            )
        )
        self.bands_dataframe = data

    def is_expanding(self, at):
        return self.bands_dataframe['change'][at] == 1

    def is_contracting(self, at):
        return self.bands_dataframe['change'][at] == -1

    def is_stable(self, at):
        return self.bands_dataframe['change'][at] == 0

    def is_uptrend(self):
        pass

    def is_downtrend(self):
        pass
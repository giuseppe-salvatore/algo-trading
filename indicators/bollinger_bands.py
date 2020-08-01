import pandas as pd


def add_bollinger_band(dataframe, on_field, mean_window, std_window):
    dataframe['5 min mean'] = dataframe['Close'].rolling(window=mean_window).mean()
    dataframe['UpperBB'] = dataframe['5 min mean'] + 2*dataframe['Close'].rolling(window=5).std()
    dataframe['LowerBB'] = dataframe['5 min mean'] - 2*dataframe['Close'].rolling(window=5).std()
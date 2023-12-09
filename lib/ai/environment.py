import numpy as np
import pandas as pd


from lib.util.logger import log
from lib.market_data_provider.provider_utils import MarketDataProviderUtils
from lib.market_data_provider.market_data_provider import MarketDataProvider

# Define the stock symbol and date range for data collection
stock_symbol = 'AAPL'  # Example: Apple Inc.
start_date = '2021-01-01'
end_date = '2022-01-01'

# Fetch historical stock data from the market data provider of your choice

data_provider = MarketDataProviderUtils.get_provider("Alpaca")
data = data_provider.get_minute_candles(symbol,
                                        start_date,
                                        end_date,
                                        force_provider_fetch=False,
                                        store_fetched_data=True)
stock_data = MarketDataProvider()

# Preprocess the data
def preprocess_data(data):
    # Calculate additional features if needed (e.g., moving averages, RSI, etc.)
    data['SMA_60'] = data['Close'].rolling(window=50).mean()  # Example: 60-minute Simple Moving Average

    # Drop rows with NaN values
    data.dropna(inplace=True)

    return data


# Preprocess the stock data
processed_data = preprocess_data(stock_data)

# Define the stock market environment for reinforcement learning
class StockMarketEnv:
    def __init__(self, data):
        self.data = data
        self.current_step = 0
        self.total_steps = len(data) - 1  # Number of steps is the length of data - 1

    def reset(self):
        self.current_step = 0
        return self.data.iloc[self.current_step]

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= self.total_steps

        if done:
            next_state = None
            reward = 0  # Define your reward mechanism here based on actions and market movement
        else:
            next_state = self.data.iloc[self.current_step]
            reward = 0  # Define your reward mechanism here based on actions and market movement

        return next_state, reward, done

    def get_action_space(self):
        # Define your action space (buy, sell, hold, etc.)
        return ['BUY', 'SELL', 'HOLD']  # Example action space


# Initialize the stock market environment
env = StockMarketEnv(processed_data)

# Test the environment
initial_state = env.reset()
print("Initial State:")
print(initial_state)

# Example of taking an action in the environment
action_space = env.get_action_space()
random_action = np.random.choice(action_space)  # Choosing a random action for demonstration
next_state, reward, done = env.step(random_action)
print("\nAfter Taking Action:", random_action)
print("Next State:")
print(next_state)
print("Reward:", reward)
print("Done:", done)

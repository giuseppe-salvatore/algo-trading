import numpy as np
import pandas as pd

from datetime import datetime
from lib.util.logger import log
from lib.market_data_provider.provider_utils import MarketDataProviderUtils


# Define the stock market environment for reinforcement learning
class StockMarketEnv:
    def __init__(self, data):
        self.data = data
        self.current_step = 0
        self.total_steps = len(data) - 1  # Number of steps is the length of data - 1
        self.shares = 0
        self.buy_price = 0

    def reset(self):
        self.current_step = 0
        return self.data.iloc[self.current_step]

    def step(self, action):
        current_state = self.data.iloc[self.current_step]
        self.current_step += 1
        done = self.current_step >= self.total_steps

        if done:
            next_state = None
            reward = 0  # Define your reward mechanism here based on actions and market movement
        else:
            next_state = self.data.iloc[self.current_step]

            if action is 'SELL':
                profit = (current_state['close'] - self.buy_price) * self.shares
                self.shares = 0
                self.buy_price = 0
                reward = profit
                # print("Profit = {:.2f}".format(profit))
            elif action is 'BUY':
                self.buy_price = current_state['close']
                self.shares = 10
                reward = 0
                # print("Bought at " + str(self.buy_price))
            else:
                reward = 0

        return next_state, reward, done

    # def get_action_space(self):
    #     if self.stock_count > 0:
    #         return ['SELL', 'HOLD']  # Example action space
    #     if self.stock_count == 0:
    #         return ['BUY', 'HOLD']

    def get_action_space(self):
        return ['BUY', 'SELL', 'HOLD']  # Example action space


# Initialize the stock market environment


# Test the environment
# initial_state = env.reset()
# print("Initial State:")
# print(initial_state)

# Example of taking an action in the environment
# action_space = env.get_action_space()
# random_action = np.random.choice(action_space)  # Choosing a random action for demonstration
# next_state, reward, done = env.step(random_action)


# for i in range(0, 10000):
#     if i == 50:
#         next_state, reward, done = env.step('BUY')
#         print("\nAfter Taking Action:", 'BUY')
#         print("Next State:")
#         print(next_state)
#         print("Reward:", reward)
#         print("Done:", done)
#     elif i == 8000:
#         next_state, reward, done = env.step('SELL')
#         print("\nAfter Taking Action:", 'SELL')
#         print("Next State:")
#         print(next_state)
#         print("Reward:", reward)
#         print("Done:", done)
#     else:
#         next_state, reward, done= env.step('HOLD')

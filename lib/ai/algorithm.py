import pandas as pd
import numpy as np
import tensorflow as tf

from lib.ai.environment import StockMarketEnv

# Neural Network model for Q-learning
class QNetwork(tf.keras.Model):

    def __init__(self, num_actions):
        super(QNetwork, self).__init__()
        self.dense1 = tf.keras.layers.Dense(32, activation='relu')
        self.dense2 = tf.keras.layers.Dense(32, activation='relu')
        self.output_layer = tf.keras.layers.Dense(num_actions)

        self.epsilon = 0.9  # Exploration rate
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.shares = 0

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.output_layer(x)

    def get_action_space(self, shares):
        if shares > 0:
            return ['SELL', 'HOLD']
        else:
            return ['BUY', 'HOLD']

    # Function to choose action using Q-network
    def choose_action(self, state, shares):
        action_space = ['BUY', 'SELL', 'HOLD']
        if np.random.uniform(0, 1) < self.epsilon:
            # Explore: Choose a random action
            if shares == 0:
                action = np.random.choice(['BUY', 'HOLD'])
            else:
                action = np.random.choice(['SELL', 'HOLD'])
        else:
            # Exploit: Choose action with highest Q-value from the network
            state_array = np.array([state.values])  # Convert state to numpy array
            q_values = self(state_array.astype(np.float32)).numpy()[0]
            action_index = np.argmax(q_values)
            action = action_space[action_index]

        return action

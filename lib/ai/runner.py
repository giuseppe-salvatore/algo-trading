import numpy as np
import pandas as pd
import tensorflow as tf
from datetime import datetime
from lib.util.logger import log
from lib.ai.algorithm import QNetwork
from lib.ai.environment import StockMarketEnv
from lib.market_data_provider.provider_utils import MarketDataProviderUtils

def get_data_for(symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    data_provider = MarketDataProviderUtils.get_provider("Alpaca")
    data = data_provider.get_minute_candles(symbol,
                                            start_date,
                                            end_date,
                                            force_provider_fetch=False,
                                            store_fetched_data=False)

    # Calculate additional features if needed (e.g., moving averages, RSI, etc.)
    data['SMA_60'] = data['close'].rolling(window=50).mean()  # Example: 60-minute Simple Moving Average

    # Drop rows with NaN values
    data.dropna(inplace=True)
    data.reset_index(drop=True, inplace=True)
    data.drop(columns='ny_datetime', inplace=True, errors='ignore')
    data.drop(columns='timestamp', inplace=True, errors='ignore')
    data.drop(columns='symbol', inplace=True, errors='ignore')
    data.drop(columns='trade_count', inplace=True, errors='ignore')
    data.drop(columns='vwap', inplace=True, errors='ignore')
    data.drop(index=0, inplace=True, errors='ignore')

    print(data)

    return data


if __name__ == "__main__":

    # Create the data for the execution
    training_stock_data = get_data_for(
        symbol='AAPL',
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 5, 1)
    )

    print(tf.config.experimental.list_physical_devices())
    print(tf.config.experimental.list_logical_devices())

    env = StockMarketEnv(training_stock_data)

    # Q-learning parameters
    num_episodes = 500  # Number of episodes (iterations)

    # Initialize Q-network and optimizer
    action_space = env.get_action_space()
    num_actions = len(['BUY', 'SELL', 'HOLD'])
    state_space = len(env.data.columns)

    q_network = QNetwork(num_actions)
    optimizer = tf.keras.optimizers.Adam(learning_rate=q_network.alpha)

    # Q-learning training loop
    for episode in range(num_episodes):
        state = env.reset()
        total_reward = 0

        while True:
            action = q_network.choose_action(state, env.shares)
            next_state, reward, done = env.step(action)

            if done:
                break

            state_array = np.array([state.values])
            next_state_array = np.array([next_state.values])

            # Calculate target Q-value
            target = reward + q_network.gamma * np.max(q_network(next_state_array.astype(np.float32)).numpy()[0])

            # Calculate current Q-value
            with tf.GradientTape() as tape:
                predicted = q_network(state_array.astype(np.float32))
                predicted_value = predicted[0][action_space.index(action)]
                loss = tf.reduce_mean(tf.square(target - predicted_value))

            # Backpropagation
            grads = tape.gradient(loss, q_network.trainable_variables)
            optimizer.apply_gradients(zip(grads, q_network.trainable_variables))

            total_reward += reward
            state = next_state

        print(f"Episode {episode + 1}: Total Reward = {total_reward}")

        # Evaluation: Choose action for a given state using the trained Q-network
        state_to_evaluate = env.data.iloc[-1]  # Consider the last state for evaluation
        chosen_action = q_network.choose_action(state_to_evaluate, env.shares)
        print("\nChosen Action for Evaluation:")
        print(chosen_action)

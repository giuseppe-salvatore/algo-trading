
import itertools
from api_proxy import TradeApiProxy
from strategies.scalping.run import DummyScalping


if __name__ == "__main__":

    api = TradeApiProxy()

    reward_perc = range(10, 15)
    stop_loss_perc = range(5, 10)
    enter_per_variation_signal = range(2, 10)

    index = 0
    results = {}
    for xs in itertools.product(reward_perc, stop_loss_perc, enter_per_variation_signal):
        print("Run " + str(index) + " params:" + str(xs), end="")
        strategy = DummyScalping()
        strategy.params["reward_perc"] = float(xs[0]) / 10.0
        strategy.params["stop_loss_perc"] = float(xs[1]) / 10.0
        strategy.params["enter_per_variation_signal"] = float(xs[2]) / 10.0
        gain = strategy.run_strategy(api)
        print(" result = " + str(gain))
        results[index] = {"params": xs, "gain": gain}
        index += 1

    # strategy = DummyScalping()
    #
    # strategy.params["reward_perc"] = 3.0
    # strategy.params["stop_loss_perc"] = 0.5
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 1.0
    # strategy.params["stop_loss_perc"] = 0.5
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 1.5
    # strategy.params["stop_loss_perc"] = 0.5
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 2.0
    # strategy.params["stop_loss_perc"] = 0.5
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 2.5
    # strategy.params["stop_loss_perc"] = 0.5
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 1
    # strategy.params["stop_loss_perc"] = 1
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 1.5
    # strategy.params["stop_loss_perc"] = 1
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 2
    # strategy.params["stop_loss_perc"] = 1
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["reward_perc"] = 2.5
    # strategy.params["stop_loss_perc"] = 1
    # strategy.params["enter_per_variation_signal"] = 0.5
    # strategy.run_strategy(api)

    # strategy = DummyScalping()
    # strategy.params["day"] = 30
    # strategy.params["reward_perc"] = 0.9
    # strategy.params["stop_loss_perc"] = 0.2
    # strategy.params["enter_per_variation_signal"] = 0.3
    # strategy.run_strategy(api)

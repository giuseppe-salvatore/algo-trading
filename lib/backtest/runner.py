import yaml
import json
import argparse
import importlib
import pandas as pd
import multiprocessing as mp
from lib.util.logger import log
from lib.strategies.base import BacktestStrategy


def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", "-c", help="Path to the configuration file")
    parser.add_argument("--log-level", "-l", default="INFO",
                        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    args = parser.parse_args()

    pd.set_option("mode.chained_assignment", None)
    parallel_process = mp.cpu_count() - 1

    config = load_config(args.config_file)

    log.info(json.dumps(config, indent=2))

    strategy_class_name = config.get("strategy_class")
    module_name = config.get("module")
    package_name = config.get("package")

    try:
        strategy_module = importlib.import_module(f"{package_name}.{module_name}")
        strategy_class = getattr(strategy_module, strategy_class_name)
        config["params"]["Strategy"] = strategy_class
    except (ImportError, AttributeError) as e:
        log.error(f"Error importing strategy class: {e}")
        return

    backtest = BacktestStrategy()
    log.info(f"Setting log level to {args.log_level}")
    log.setLevel(args.log_level)
    log.debug("Selected {} strategy".format(strategy_class.get_name()))

    params = config.get("params", {})
    backtest = BacktestStrategy()
    symbols = config.get("symbols")
    backtest.run_simulation(symbols, params, parallel_process)


if __name__ == "__main__":
    main()

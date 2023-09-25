![Unit Tests](https://bitbucket.org/gr4ce/algo-trading/downloads/unit_test_count.svg)
![Pass Rate](https://bitbucket.org/gr4ce/algo-trading/downloads/pass_rate.svg)
![Code Coverage](https://bitbucket.org/gr4ce/algo-trading/downloads/code_coverage.svg)
![BDD](https://bitbucket.org/gr4ce/algo-trading/downloads/bdd_pass_rate.svg)

# Algorithmic Trading Bot #

### Reason for this project ###

* Understand a bit more about the world of financial trading
* Enter the world of AI/Machine Learning
* Trying to make some money more than shitty ISAs

### Dependencies ###

* Alpaca Trading and Alpaca Stock Data API are used https://alpaca.markets/
* The stock API uses REST but soon it's going to transition to websocket

### Getting Started ###

The project uses a Makefile to run some basic targets. For more complex executions you will
have to run individual scripts and passing parameters based on your needs

### Run strategies ###

Here is an example on how to run a strategy 
```
python -m lib.backtest.backtester lib.strategies dummy DummyStrategy
```

### Tests ###

Unit tests are provided in tests/ folder. To run simply 
```
pytest -v tests/trade_simulation_test.py
```
Note: you need to create an environment

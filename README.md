![Unit Tests](https://bitbucket.org/gr4ce/algo-trading/downloads/unit_test_count.svg)
![Pass Rate](https://bitbucket.org/gr4ce/algo-trading/downloads/pass_rate.svg)
![Code Coverage](https://bitbucket.org/gr4ce/algo-trading/downloads/code_coverage.svg)
![BDD](https://bitbucket.org/gr4ce/algo-trading/downloads/bdd_pass_rate.svg)

# Algorithmic Trading Bot #

### Reason for this project ###

* Understand a bit more about the world of financial trading
* Enter the world of AI/Machine Learning
* Trying to make some money more than shitty ISAs

## Dependencies ##

* Alpaca Trading and Alpaca Stock Data API are used https://alpaca.markets/
* The stock API uses REST but soon it's going to transition to websocket

## Getting Started ##

The project uses a Makefile to run some basic targets. For more complex executions you will
have to run individual scripts and passing parameters based on your needs.

For most of the end targets (below sections) you won't need to run the preparation steps as they are included but if you need you have the prepare and install targets

```
make prepare
```
and
```
make install
```

## Tests ##

Use make for this, you can run unit and acceptance tests
```
make unit-test
```
and
```
make acceptance-test
```

## Code Coverage ##
Again use make for this:
```
make coverage
```

## Running strategies ##

Here is an example on how to run a strategy, there is no make target yet but will add one soon. Also I will need to add better documentation on parameters and how to setup a new strategy
```
python -m lib.backtest.runner lib.strategies dummy DummyStrategy
```

## Updating the local db with latest bars ##

```
make clean   // will clean a few folders
make pull    // will pull the actual data from the alpaca API and store it in a tmp folder
make store   // will store the data in the db
make db-info // will grab the info regarding the symbols in the db
```

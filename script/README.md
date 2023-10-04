Useful scripts to perform some boring actions

`bar_pull.py`  
**Description**: Gathers minute candles from Finhhub API  
**Usage**: `python -m script.bar_pull [symbol_list]` (if symbol_list is not provided it will use the watchlist)

`get_cache_period.py`  
**Description**: Tells the stocks that you have data for and the density of the data per day  
**Usage**: `python -m script.get_cache_period [symbol_list]` (if symbol_list is not provided it will use the watchlist)bash run_rabbit_service.sh

`alpaca_market_data_pull.py`  
**Description**: Pulls minute bars from alpaca data source. You will need to have a funded account (subscription is however free) to be able to use this. If you run it on the beginning of each month it will pull the minute bars for a set of stocks picked up from `stocklists/` for the previous entire month and will store the data in form of an INSERT DDL in a file per each symbol plus one big file with all the symbols, so you can use what you prefer to add it to the database.  
The job has been added to Makefile target so you also use `make pull`
**Usage**: `python -m script.alpaca_market_data_pull`
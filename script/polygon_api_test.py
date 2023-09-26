import market_data_provider.tiingo_proxy
import market_data_provider.polygon_proxy
import market_data_provider.finnhub_proxy
import market_data_provider.marketstack_proxy
import market_data_provider.alphavantage_proxy
import market_data_provider.financial_modeling

#market_data_provider.polygon_proxy.get_minute_bars("AAPL", "2020-05-07", "2020-05-10")

#market_data_provider.marketstack_proxy.get_minute_bars("AAPL", "2020-05-06", "2020-05-10")

#market_data_provider.alphavantage_proxy.get_minute_bars("AAPL", "2020-05-06", "2020-05-10")

#market_data_provider.tiingo_proxy.get_minute_bars("AAPL", "2020-05-06", "2020-05-10")

#market_data_provider.financial_modeling.get_minute_bars("AAPL", "2020-05-06", "2020-05-10")

market_data_provider.finnhub_proxy.get_minute_bars("AAPL", "2019-09-25",
                                                   "2019-09-26")

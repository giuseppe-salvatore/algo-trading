from lib.market_data_provider.finnhub import FinnhubDataProvider
from lib.market_data_provider.polygon import PolygonDataProvider


class MarketDataProviderUtils:
    @staticmethod
    def get_available_providers():
        return ["Finnhub", "Polygon", "Tiingo", "Alpaca"]

    @staticmethod
    def get_provider(provider_name: str):
        """
        Returns an instance of the market data provider passed as string.
        Currently supported data providers are:
        - Finnhub
        - Polygon
        """
        if provider_name == "Finnhub":
            return FinnhubDataProvider()
        elif provider_name == "Polygon":
            return PolygonDataProvider()
        elif provider_name == "Alpaca":
            return AlpacaDataProvider()
        else:
            raise ValueError("No provider avaialbe named: {}".format(provider_name))

import json
import pandas as pd
import datetime as dt
import requests as req
import datetime as dt


class MarketDataProvider():

    def __init__(self):
        self.base_url = None
        self.provider_name = None
        self.provider_url = None

    def set_provider_name(self, name: str):
        self.provider_name = name

    def get_provider_name(self):
        return self.provider_name

    def set_provider_url(self, url: str):
        self.provider_url = url

    def get_provider_url(self):
        return self.provider_url

    def set_base_url(self, url: str):
        self.base_url = url

    def get_base_url(self):
        return self.base_url

    def append_params(self, url: str, params: dict = None):
        url += "?" + self.get_key_name() + "=" + self.get_key_value()
        if params != None:
            for key in params:
                url += "&" + key + "=" + str(params[key])
        return url

    def get(self, endpoint: str, params: dict = None):
        url = self.get_base_url() + endpoint
        url = self.append_params(url, params)
        resp = req.get(url)
        if resp.status_code != 200:
            raise Exception("Error perfoming GET request to url: " +
                            url + "\nException message: " + str(resp.content))
        return json.loads(resp.content)

    def get_key_name(self):
        pass

    def get_key_value(self):
        pass

    def get_minute_candles(self, symbol: str, start_date: dt.datetime, end_date: dt.datetime):
        pass

    def get_day_candles(self, symbol: str, start_date: dt.datetime, end_date: dt.datetime):
        pass

    def get_news(self):
        print("WARNING: The get_news() API is not supported not free on " + self.provider_name)

    def get_supported_symbols(self):
        print("WARNING: The get_supported_symbols() API is not supported not free on " + self.provider_name)

    def get_symbol_details(self, symbol: str):
        print("WARNING: The get_symbol_details() API is not supported not free on " + self.provider_name)

    def get_financials(self, symbol: str):
        print("WARNING: The get_financials() API is not supported not free on " + self.provider_name)

import json
import config
import datetime
import requests
from market_data_provider.market_data_provider import MarketDataProvider


ticks_endpoint = "/v2/ticks/stocks/nbbo"
aggregates_endpoint = "/v2/aggs/ticker"
financials_endpoint = "/v2/reference/financials"
ticker_type_endpoint = "/v2/reference/types"
symbol_details_endpoint = "/v1/meta/symbols/"
supported_tickers_endpoint = "/v2/reference/tickers"



class PolygonDataProvider(MarketDataProvider):

    def __init__(self):
        self.set_provider_name("Polygon")
        self.set_provider_url("https://polygon.io")
        self.set_base_url("https://api.polygon.io")

    def get_minute_candles(self, symbol: str, start_date:datetime.datetime, end_date:datetime.datetime):

        print("Getting minute candles on " + self.get_provider_name() + " api")
        endpoint = "/aggs/ticker/" + symbol + "/range/1/minute/" + start_date + "/" + end_date
        
        response = self.get(endpoint)
        content = json.loads(response.content)

        print(json.dumps(content, indent=4))
        count = 0
        for elem in content["results"]:
            date_time = datetime.datetime.fromtimestamp(float(elem["t"])/1000)

            if date_time >= datetime.datetime.strptime(start_date + " 06:00", '%Y-%m-%d %H:%M') and \
                    date_time <= datetime.datetime.strptime(start_date + " 22:30", '%Y-%m-%d %H:%M'):
                print(date_time)
                count += 1

        print("Count " + str(count))

    def get_day_candles(self, symbol: str, start_date:datetime.datetime, end_date:datetime.datetime):
        pass

    def get_news(self):
        pass

    def get_supported_symbols(self):
        pass

    def get_key_name(self):
        return "apiKey"

    def get_key_value(self):
        return config.POLYGON_API_KEY

    def get_symbol_details(self, symbol: str):
        return self.get(symbol_details_endpoint + symbol + "/company")

    def get_financials(self, symbol):
        response = self.get(
            financials_endpoint + "/" + symbol,
            { "limit": 1 }
        )

        json_content = json.loads(response.content)
        if "results" not in json_content:
            raise Exception(
                "Error parsing response: expected 'results' in content but not found\nResponse Content: ")

        if "status" not in json_content:
            raise Exception(
                "Error in json response: expected key 'status' but not present")

        if json_content["status"] != "OK":
            raise Exception("Error in json response: expected 'status' to be 'OK'")

        return json_content["results"]

    def get_supported_symbols(self, type: str = None):
        page = 1
        results = []
        first_call = True
        pages = 10 # We use a temp value just to fetch the actual number of pages
        ticker_type = {}
        while page <= pages:
            if first_call:
                result = self.get_supported_tickers_page(page,type)
                count = result["count"]
                pages = int(count / 50) + 1
                print("Total count " + str(count) + " fetching " + str(pages) + " pages")
                results += result["tickers"]
                first_call = False
            else:
                result = self.get_supported_tickers_page(page,type)
                results += result["tickers"]

            page = result["page"]
            print("Fetching page " + str(page) + "/" + str(pages) + " result page = " + str(result["page"]))
            page += 1
            for elem in result["tickers"]:
                if "type" in elem:
                    if elem["type"] in ticker_type:
                        ticker_type[elem["type"]] += 1
                    else:
                        ticker_type[elem["type"]] = 1
            print(ticker_type)
    
        return results

    def get_supported_tickers_page(self, page: int, type: str = None):

        params = {
            "perpage": 50,
            "page": page,
            "active": "true",
            "locale": "us",
            "market": "STOCKS"
        }
        if type != None:
            params["type"] = type        

        return self.get(supported_tickers_endpoint, params)        
        











# def get_ticker_types():
#     url = polygon_base_api_url + ticker_type_endpoint 
#     url = append_params(url)

#     response = requests.get(url)
#     if response.status_code != 200:
#         raise Exception("Error perfoming GET request to url: " +
#                         url + "\nException message: " + response.content)
#     json_content = json.loads(response.content)
#     if "status" in json_content:
#         if json_content["status"] == "OK":
#             if "results" in json_content:
#                 return json_content["results"]
#     print("Error parsing the response " + json.dumps(json_content,indent=4))

# def get_market_cap(symbol: str):
#     financials = get_financials(symbol)
#     if len(financials) > 0:
#         if "marketCapitalization" not in financials[0]:
#             raise Exception(
#                 "Error parsing financials: expected 'marketCapitalization' in object but not found\nResponse Content: " + str(financials))
#         else:
#             return financials[0]["marketCapitalization"]
#     return None


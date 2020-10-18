
import csv
import requests
import conf.secret as config

alphavantage_base_api_url = "https://www.alphavantage.co/query?function="
intraday_function = "TIME_SERIES_INTRADAY"
intraday_function_ext = "TIME_SERIES_INTRADAY_EXTENDED"


def append_params(url: str, params):

    url += "&apikey=" + params['apikey']
    for elem in params:
        if elem == "apikey":
            continue
        url += "&" + elem + "=" + params[elem]

    return url


# def get_minute_bars(symbol: str, time_from: str, time_to: str):
#     url = alphavantage_base_api_url + intraday_function
#     url = append_params(url, {
#         "symbol": "AAPL",
#         "apikey": config.ALPHAVANTAGE_FREE_API_KEY,
#         "interval": "1min"
#     })
#     print(url)
#     response = requests.get(url)
#     content = json.loads(response.content)
#     print(json.dumps(content,indent=4))


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = alphavantage_base_api_url + intraday_function_ext
    url = append_params(url, {
        "symbol": "AAPL",
        "apikey": config.ALPHAVANTAGE_FREE_API_KEY,
        "interval": "1min",
        "slice": "year1month1"
    })
    with requests.Session() as s:
        download = s.get(url)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        header = my_list[0]
        for row in reversed(my_list[1:]):
            print(row)
        print(header)

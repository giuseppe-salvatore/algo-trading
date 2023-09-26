import json
import datetime
import requests

from conf import secret as config

tiingo_base_api_url = "https://api.tiingo.com"
price_endpoint = "/iex/prices"
fundamentas_endpoint = "/fundamentals"


def append_params(url: str, params):
    url += "?token=" + params['token']
    for elem in params:
        if elem == "token":
            continue
        url += "&" + elem + "=" + params[elem]

    return url


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = tiingo_base_api_url + symbol + "/" + price_endpoint
    url = append_params(
        url, {
            "token": config.TIINGO_API_KEY,
            "resampleFreq": "1min",
            "startDate": time_from,
            "columns": "open,high,low,close,volume",
            "afterHours": "true"
        })
    print("URL: " + url)
    response = requests.get(url)
    content = json.loads(response.content)

    for elem in content:
        date = datetime.datetime.fromisoformat(elem['date'][:-1])
        print("{} {}".format(date - datetime.timedelta(hours=4),
                             elem['volume']))


def get_fundamentals(symbol: str):

    url = tiingo_base_api_url
    url += fundamentas_endpoint
    url += "/" + symbol + "/daily"
    url = append_params(
        url, {
            "token":
            config.TIINGO_API_KEY,
            "startDate":
            datetime.datetime.strftime(datetime.datetime.today(), '%Y-%m-%D')
        })

    headers = {'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception("Error: " + response.content)

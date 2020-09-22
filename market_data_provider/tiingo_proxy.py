import json
import config
import datetime
import requests

tiingo_base_api_url = "https://api.tiingo.com/iex/"
price_endpoint = "/prices"


def append_params(url: str, params):
    url += "?token=" + params['token']
    for elem in params:
        if elem == "token":
            continue
        url += "&" + elem + "=" + params[elem]

    return url


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = tiingo_base_api_url + symbol + "/" + price_endpoint
    url = append_params(url, {
        "token": config.TIINGO_API_KEY,
        "resampleFreq": "1min",
        "startDate": time_from,
        "columns": "open,high,low,close,volume",
        "afterHours" : "true"
    })
    print("URL: " + url)
    response = requests.get(url)
    content = json.loads(response.content)

    for elem in content:
        #date = datetime.datetime.strptime(elem['date'],'%Y-%m-%dT%H:%M:%S.%z')
        date = datetime.datetime.fromisoformat(elem['date'][:-1])
        print(str(date - datetime.timedelta(hours=4)) + " " + str(elem['volume']))

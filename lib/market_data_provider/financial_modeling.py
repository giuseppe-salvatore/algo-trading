import json
import requests

financial_modeling_url = "https://financialmodelingprep.com/api/v3"
minute_chart_endpoint = "/historical-chart/1min"

def append_params(url: str, params):
    url += "?apikey=" + params['apikey']
    for elem in params:
        if elem == "apikey":
            continue
        url += "&" + elem + "=" + params[elem]

    return url


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = financial_modeling_url + minute_chart_endpoint + "/" + symbol
    url = append_params(url, {
        "apikey": "demo",
        "interval": "1min"
    })

    print("URL: " + url)
    response = requests.get(url)
    content = json.loads(response.content)

    print(json.dumps(content, indent=4))

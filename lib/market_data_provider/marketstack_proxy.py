import json
import config
import requests
import datetime


marketstack_v1_base_api_url = "http://api.marketstack.com/v1"
intraday_endpoint = "/intraday"
daily_endpoint = "/eod"
tickers_endpoint = "/tickers"

#    & limit = 100
#    & offset = 0"

def append_params(url: str, params):

    url += "?access_key=" + params['access_key']
    for elem in params:
        if elem == "access_key":
            continue
        url += "&" + elem + "=" + params[elem]
    
    return url

def get_daily_bars(symbol: str, time_from: str, time_to: str):
    url = marketstack_v1_base_api_url + daily_endpoint
    url = append_params(url, {
        "symbols": "AAPL",
        "access_key": config.MARKETSTACK_FREE_API_KEY,
        "interval": "1m",
        "date_from": time_from,
        "date_to": time_to
    })

def get_tickers(symbol: str):
    url = marketstack_v1_base_api_url + tickers_endpoint + "/" + symbol
    url = append_params({"access_key": config.MARKETSTACK_FREE_API_KEY})

def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = marketstack_v1_base_api_url + intraday_endpoint + "/" + time_from
    url = append_params(url, {
        "symbols": symbol,
        "access_key": config.MARKETSTACK_FREE_API_KEY,
        "interval": "1min"
    })
    print("URL: " + url)
    response = requests.get(url)
    content = json.loads(response.content)

    print(json.dumps(content,indent=4))
    count = 0
    for elem in content["results"]:
        date_time = datetime.datetime.fromtimestamp(float(elem["t"])/1000)
        
        if date_time >= datetime.datetime.strptime(time_from + " 06:00", '%Y-%m-%d %H:%M') and \
            date_time <= datetime.datetime.strptime(time_from + " 22:30", '%Y-%m-%d %H:%M'):
            print(date_time)
            count += 1

    print("Count " + str(count))
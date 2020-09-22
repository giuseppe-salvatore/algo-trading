import json
import time
import config
import datetime
import requests


"""
Example: https://finnhub.io/api/v1/stock/candle?symbol=AAPL&resolution=1&from=1572651390&to=1572910590

Arguments:

token: apiKey

symbol: REQUIRED
Symbol.

resolution: REQUIRED
Supported resolution includes 1, 5, 15, 30, 60, D, W, M .Some timeframes might not be available depending on the exchange.

from: REQUIRED
UNIX timestamp. Interval initial value. (use datetime.datetime.fromtimestamp(from))

to: REQUIRED
UNIX timestamp. Interval end value.

format: optional
By default, format=json. Strings json and csv are accepted.

adjusted: optional
By default, adjusted=false. Use true to get adjusted data.

"""

base_api_url = "https://finnhub.io/api/v1/stock/"
bar_endpoint = "candle"


def append_params(url: str, params):    
    url += "?token=" + params['token']
    for elem in params:
        if elem == "token":
            continue
        url += "&" + elem + "=" + params[elem]
    
    return url


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = base_api_url + bar_endpoint
    url = append_params(url, {
        "symbol": symbol,
        "token": config.FINNHUB_API_KEY,
        "resolution": "1",
        "format": "json",
        "from": str(int(time.mktime(datetime.datetime.strptime(time_from, '%Y-%m-%d').timetuple()))),
        "to": str(int(time.mktime(datetime.datetime.strptime(time_to, '%Y-%m-%d').timetuple()))),
        "adjusted": "true"
    })

    print("URL: " + url)
    response = requests.get(url)
    content = json.loads(response.content)

    #print(json.dumps(content,indent=4))
    if content["s"] != "ok":
        print("No data")
        return 

    result_lengh = len(content["c"])
    result_string = ""
    count = 0
    
    for i in range(result_lengh):
        date_time = datetime.datetime.fromtimestamp(int(content["t"][i]))

        result_string +=  (str(date_time) + "," + 
            str(content["o"][i]) + "," + 
            str(content["h"][i]) + "," + 
            str(content["l"][i]) + "," + 
            str(content["c"][i]) + "," + 
            str(content["v"][i]) + "\n")
        
        if date_time >= datetime.datetime.strptime(time_from + " 14:30", '%Y-%m-%d %H:%M') and \
            date_time <= datetime.datetime.strptime(time_from + " 20:59", '%Y-%m-%d %H:%M'):
            count += 1

    print(result_string)
    print("Count is " + str(count))


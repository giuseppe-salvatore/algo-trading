import json
import config
import datetime
import requests


polygon_v2_base_api_url = "https://api.polygon.io/v2/"

url = polygon_v2_base_api_url + "ticks/stocks/nbbo/AAPL/2020-07-29?"
url = polygon_v2_base_api_url + \
    "aggs/ticker/AAPL/range/1/minute/2020-07-29/2020-07-30?"


mins = 0
# for elem in content["results"]:
#     print("Calculated")
#     print(datetime.datetime.timestamp(datetime.datetime(2020,7,29,9,mins,0)))
#     print(datetime.datetime(2020,7,29,9,mins,0))
#     print("Real")
#     print(elem["t"])
#     print(datetime.datetime.fromtimestamp(float(elem["t"])/1000000000))
#     mins += 1


def append_key(url: str):

    return url + "&apiKey=" + config.ALPACA_LIVE_API_KEY


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = polygon_v2_base_api_url + "aggs/ticker/" + symbol + \
        "/range/1/minute/" + time_from + "/" + time_to + "?"
    final_url = append_key(url)
    print("Request URL = " + final_url)
    response = requests.get(final_url)
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


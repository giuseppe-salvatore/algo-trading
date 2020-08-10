import json
import datetime
import requests

url = "https://api.polygon.io/v2/ticks/stocks/nbbo/AAPL/2020-07-29?apiKey=PK87CIAN71CNJXDUBS0B&limit=10"
url = "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/minute/2020-07-29/2020-07-30?apiKey=PK87CIAN71CNJXDUBS0B"
response = requests.get(url)

content = json.loads(response.content)

mins = 0
# for elem in content["results"]:    
#     print("Calculated")
#     print(datetime.datetime.timestamp(datetime.datetime(2020,7,29,9,mins,0)))
#     print(datetime.datetime(2020,7,29,9,mins,0))
#     print("Real")
#     print(elem["t"])
#     print(datetime.datetime.fromtimestamp(float(elem["t"])/1000000000))
#     mins += 1


for elem in content["results"]: 
    print(datetime.datetime.fromtimestamp(float(elem["t"])/1000000000))
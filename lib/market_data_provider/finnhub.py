import json
import time
import datetime
import requests
import pandas as pd
import conf.secret as config
from lib.market_data_provider.market_data_provider import MarketDataProvider


candle_endpoint = "/v1/stock/candle"


class FinnhubDataProvider(MarketDataProvider):

    def __init__(self):
        self.set_provider_name("Finnhub")
        self.set_provider_url("https://finnhub.io")
        self.set_base_url("https://finnhub.io/api")

    def get_key_name(self):
        return "token"

    def get_key_value(self):
        return config.FINNHUB_API_KEY

    def get_minute_candles(self, symbol: str, start_date: datetime.datetime, end_date: datetime.datetime):
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

        print("Getting minute candles on " + self.get_provider_name() + " api")

        # Finnhub uses UNIX timestapms to operate with time ranges so we need to convert to datetime
        start_date = str(
            int(time.mktime(datetime.datetime.strptime(start_date, '%Y-%m-%d').timetuple())))
        end_date = str(
            int(time.mktime(datetime.datetime.strptime(end_date, '%Y-%m-%d').timetuple())))

        endpoint = candle_endpoint
        params = {
            "symbol": symbol,
            "resolution": "1",
            "format": "json",
            "from": start_date,
            "to": end_date,
            "adjusted": "true"
        }

        res = self.get(endpoint, params)

        try:
            json_res = res.json()
        except:
            print("Response not in json format " + res.text)

        # if "results" not in json_res:
        #     raise ValueError(
        #         "Expected 'results' key in response content: " + json.dumps(json_res, indent=4))

        result_list = []
        result_lengh = len(json_res["c"])

        for i in range(result_lengh):
            date_time = datetime.datetime.fromtimestamp(int(json_res["t"][i]))

            result_list.append({
                "datetime": date_time.strftime("%Y-%m-%d %H:%M"),
                "Open": json_res["o"][i],
                "High": json_res["h"][i],
                "Low": json_res["l"][i],
                "Close": json_res["c"][i],
                "Volume": json_res["v"][i]
            })

            # if date_time >= datetime.datetime.strptime(start_date + " 06:00", '%Y-%m-%d %H:%M') and \
            #         date_time <= datetime.datetime.strptime(start_date + " 22:30", '%Y-%m-%d %H:%M'):

        df = pd.DataFrame(result_list)
        df.set_index("datetime", inplace=True)
        df.index = pd.to_datetime(df.index)
        return df


def get_minute_bars(symbol: str, time_from: str, time_to: str):
    url = base_api_url + bar_endpoint
    url = append_params(url, {
        "symbol": symbol,
        "resolution": "1",
        "format": "json",
        "from": str(int(time.mktime(datetime.datetime.strptime(time_from, '%Y-%m-%d').timetuple()))),
        "to": str(int(time.mktime(datetime.datetime.strptime(time_to, '%Y-%m-%d').timetuple()))),
        "adjusted": "true"
    })

    # print("URL: " + url)
    response = requests.get(url)
    if (response.status_code != 200):
        print("Response status code is: " + str(response.status_code))
        time.sleep(10)
    content = json.loads(response.content)

    # print(json.dumps(content,indent=4))
    if content["s"] != "ok":
        print("No data")
        return None

    result_lengh = len(content["c"])
    result_string = ""
    market_count = 0
    extra_count = 0

    result_list = []

    for i in range(result_lengh):
        date_time = datetime.datetime.fromtimestamp(int(content["t"][i]))

        result_list.append((symbol, date_time.strftime(
            "%Y-%m-%d %H:%M"), content["o"][i], content["h"][i], content["l"][i], content["c"][i], content["v"][i]))
        # result_string +=  (str(date_time) + "," +
        #     str(content["o"][i]) + "," +
        #     str(content["h"][i]) + "," +
        #     str(content["l"][i]) + "," +
        #     str(content["c"][i]) + "," +
        #     str(content["v"][i]) + "\n")

        if date_time >= datetime.datetime.strptime(time_from + " 14:30", '%Y-%m-%d %H:%M') and \
                date_time <= datetime.datetime.strptime(time_from + " 20:59", '%Y-%m-%d %H:%M'):
            market_count += 1

        if (date_time >= datetime.datetime.strptime(time_from + " 00:00", '%Y-%m-%d %H:%M') and
            date_time <= datetime.datetime.strptime(time_from + " 14:29", '%Y-%m-%d %H:%M')) or \
            (date_time >= datetime.datetime.strptime(time_from + " 21:00", '%Y-%m-%d %H:%M') and
             date_time <= datetime.datetime.strptime(time_from + " 23:59", '%Y-%m-%d %H:%M')):
            extra_count += 1

    return {"market": market_count,
            "extra_hours": extra_count,
            "data": result_list}

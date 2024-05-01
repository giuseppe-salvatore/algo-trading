from conf.secret import (
    # ALPHAVANTAGE_FREE_API_KEY_01,
    ALPHAVANTAGE_FREE_API_KEY_02,
    # ALPHAVANTAGE_FREE_API_KEY_03,
    # ALPHAVANTAGE_FREE_API_KEY_04,
    # ALPHAVANTAGE_FREE_API_KEY_05,
    # ALPHAVANTAGE_FREE_API_KEY_06,
    # ALPHAVANTAGE_FREE_API_KEY_07,
    # ALPHAVANTAGE_FREE_API_KEY_08,
    # ALPHAVANTAGE_FREE_API_KEY_09,
)
import os
import sys
import requests
import pandas as pd

from io import StringIO
from datetime import datetime

import lib.util.perf_timer as timer
from lib.util.logger import log


def print_sql_transaction(df, symbol):
    dest_str = ""

    for index, elem in df.iterrows():
        dest_str += '("{}","{}",{:3.2f},{:3.2f},{:3.2f},{:3.2f},{:.0f}),\n'.format(
            symbol,
            index,
            elem["open"],
            elem["close"],
            elem["high"],
            elem["low"],
            elem["volume"],
        )

    return dest_str


def get_df_from_csv(resp):
    timer.start("Read CSV")
    if resp is not None:
        df = pd.read_csv(StringIO(str(resp.content.decode("utf-8"))), sep=",")
    else:
        df = pd.read_csv("MT.alphavantage.data.csv")

    timer.stop("Read CSV")
    timer.print_elapsed("Read CSV")

    return df


months = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


class APIKeyManager:
    def __init__(self):
        self.current_api_key_idx = 0
        self.api_keys = [ALPHAVANTAGE_FREE_API_KEY_02]

    def get_api_key(self):
        if self.current_api_key_idx < len(self.api_keys):
            print("Using key: " + str(self.api_keys[self.current_api_key_idx]))
            return str(self.api_keys[self.current_api_key_idx])
        else:
            raise AllApiKeyUsed(
                "API Keys exhausted for today, Alphavantage has a limit per day"
            )

    def use_next_api_key(self):
        self.current_api_key_idx = self.current_api_key_idx + 1
        print("Switching to next API Key with idx " + str(self.current_api_key_idx + 1))


error_messages = {
    "apikey_exhausted": "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day"
}


class ApiKeyExhaustedException(Exception):
    pass


class AllApiKeyUsed(Exception):
    pass


alphavantage_base_api_url = "https://www.alphavantage.co/query?function="
intraday_function = "TIME_SERIES_INTRADAY"


def append_params(url: str, params):
    url += "&apikey=" + params["apikey"]
    for elem in params:
        if elem == "apikey":
            continue
        url += "&" + elem + "=" + params[elem]

    return url


SQL_INSERT_FILE_FORMAT = "data/alphavantage/sql/{}-{}.sql"


def get_date_str(date: datetime) -> str:
    if date is None:
        return str(datetime.now())[:7]
    else:
        return str(date)[:7]


def get_sql_insert_from_df(df, symbol: str, year: str, month: str):
    dest_file_name = SQL_INSERT_FILE_FORMAT.format(symbol, year + "-" + month)

    timer.start("Get SQL INSERT statement")

    with open(dest_file_name, "w") as dest_file:
        dest_str = "BEGIN TRANSACTION;\n"
        dest_str += (
            "INSERT INTO minute_bars (symbol,time,open,close,high,low,volume) VALUES\n"
        )

        dest_str += print_sql_transaction(df, symbol)

        dest_str = ";".join(dest_str.rsplit(",", 1))
        dest_str += "COMMIT;\n"

        dest_file.write(dest_str)

    timer.stop("Get SQL INSERT statement")
    timer.print_elapsed("Get SQL INSERT statement")


"""
Gets minute bars from Alphavantage API by month
You can easily pass the symbol and year-month

:param symbol:
:param year: a string value for the target year
:param month: a string value for the target month (as number, example: Jan will be 01)
"""


def get_minute_bars_by_month(symbol: str, year: str, month: str):
    completed = False
    while not completed:
        try:
            url = alphavantage_base_api_url + intraday_function
            url = append_params(
                url,
                {
                    "symbol": symbol,
                    "apikey": apikey_manager.get_api_key(),
                    "interval": "1min",
                    "month": year + "-" + month,
                    "outputsize": "full",
                    "adjusted": "false",
                    "datatype": "csv",
                },
            )

            with requests.Session() as s:
                log.info(
                    "Pulling data for {} year {} and month {}".format(
                        symbol, year, month
                    )
                )
                log.debug(url)
                res = s.get(url)

                if res.status_code != 200:
                    raise Exception(
                        "Error fetching data from Alphavantage API: status code = " +
                        str(res.status_code)
                    )

                content = res.content.decode("utf-8")
                if "Information" in content:
                    raise ApiKeyExhaustedException(content)

                if "Error" in content:
                    raise Exception(content)

                df = get_df_from_csv(res)

                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.set_index(pd.DatetimeIndex(df["timestamp"]))
                df.drop(columns=["timestamp"], inplace=True)

                completed = True
                return df

        except ApiKeyExhaustedException as e:
            # We can handle this
            log.warning("ApiKeyExhaustedException: " + str(e))
            apikey_manager.use_next_api_key()
        except AllApiKeyUsed as e:
            log.error("AllApiKeyUsed")
            completed = True
            raise e
        except Exception as e:
            log.error("Exception: " + str(e))
            completed = True
            raise e


def generate_required_stocks(_from: datetime, _to: datetime):
    required_stocks = []
    stock_format = "{}-{}"

    year = _from.year
    while year >= _to.year:
        from_month = 12
        if year == _from.year:
            from_month = _from.month

        to_month = 1
        if year == _to.year:
            to_month = _to.month

        month = from_month
        while month >= to_month:
            with open("stocklists/master-watchlist-reduced.txt", "r") as watchlist:
                for symbol in watchlist:
                    if "#" in symbol:
                        continue
                    required_stocks.append(
                        stock_format.format(
                            symbol[:-1], get_date_str(datetime(year, month, 1))
                        )
                    )
            month -= 1
        year -= 1

    return required_stocks


apikey_manager = APIKeyManager()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise Exception(
            """usage: python -m lib.market_data_provider.alphavantage
            \"start\" \"end\"\nexample: python -m lib.market_data_provider.alphavantage
            \"2015-12\" \"2010-01\" (note from recent to older)"""
        )

    from_date = datetime.strptime(sys.argv[1] + "-01", "%Y-%m-%d")
    to_date = datetime.strptime(sys.argv[2] + "-01", "%Y-%m-%d")

    stocks = generate_required_stocks(from_date, to_date)

    for el in stocks:
        if os.path.isfile("data/alphavantage/sql/" + str(el) + ".sql"):
            pass
        else:
            tokens = el.split("-")
            symbol = tokens[0]
            year = tokens[1]
            month = tokens[2]

            try:
                df = get_minute_bars_by_month(symbol, year, month)

            except AllApiKeyUsed as e:
                log.error(e)
                break
            except Exception as e:
                log.error(e)
                continue
            get_sql_insert_from_df(df, symbol, year, month)

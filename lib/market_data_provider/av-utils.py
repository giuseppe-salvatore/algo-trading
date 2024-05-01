import os

from datetime import datetime

def get_date_str(date: datetime) -> str:
    if date is not None:
        return str(date)[:7]
    else:
        return str(datetime.now())[:7]


if __name__ == "__main__":

    dataset = []
    for year in reversed(range(2001, 2017)):
        for month in range(1, 13):
            with open("stocklists/master-watchlist-reduced.txt", "r") as symbols:
                for symbol in symbols:
                    entry = "{}-{}".format(
                        symbol[:-1],
                        get_date_str(datetime(year, month, 1))
                    )
                    dataset.append(entry)

    for el in dataset:
        if os.path.isfile("data/alphavantage/sql/{}.sql".format(el)):
            print("Skipping {} as it exists!".format(el))

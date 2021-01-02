import pytz
import json
import sqlite3
import pandas as pd
import conf.secret as config
import lib.db.queries as queries
import matplotlib.pyplot as plt

from sqlite3 import Error
from datetime import datetime
from alpaca_trade_api import StreamConn
from lib.util.logger import log
from lib.trading.alpaca import AlpacaTrading


class Order():
    def __init__(self, order_json):

        if 'event' in order_json:
            order_json = order_json['order']

        # Order info
        self.status = order_json['status']
        self.id = order_json['id']
        self.type = order_json['type']
        self.side = order_json['side']
        self.order_type = order_json['order_type']
        self.order_class = order_json['order_class']
        self.time_in_force = order_json['time_in_force']
        self.client_id = order_json['client_order_id']

        # Asset info
        self.symbol = order_json['symbol']
        self.asset_id = order_json['asset_id']
        self.asset_class = order_json['asset_class']

        # Timing
        self.failed_at = order_json['failed_at']
        self.filled_at = order_json['filled_at']
        self.expired_at = order_json['expired_at']
        self.canceled_at = order_json['canceled_at']
        self.submitted_at = order_json['submitted_at']
        self.extended_hours = order_json['extended_hours']

        # Price info
        self.qty = order_json['qty']
        self.filled_qty = order_json['filled_qty']
        self.stop_price = order_json['stop_price']
        self.limit_price = order_json['limit_price']
        self.trail_price = order_json['trail_price']
        self.trail_percent = order_json['trail_percent']
        self.filled_avg_price = order_json['filled_avg_price']

        # Other orders
        self.replaces = order_json['replaces']
        self.replaced_by = order_json['replaced_by']
        self.replaced_at = order_json['replaced_at']

        # Complex orders
        self.legs = order_json['legs']

    def csv_header(self):
        str_data = "symbol,"
        str_data += "status,"
        str_data += "type,"
        str_data += "order_type,"
        str_data += "side,"
        str_data += "qty,"
        str_data += "limit_price,"
        str_data += "stop_price,"
        str_data += "id,"
        str_data += "client_order_id"

    def to_csv(self):
        str_data = self.symbol + ","
        str_data += self.status + ","
        str_data += self.type + ","
        str_data += self.order_type + ","
        str_data += self.side + ","
        str_data += self.qty + ","
        str_data += self.limit_price + ","
        str_data += self.stop_price + ","
        str_data += self.id + ","
        str_data += self.client_order_id
        return str_data

    def __str__(self):
        return self.to_csv()


def parse_order_file(file_name):

    f = open(file_name, "r")
    raw_orders = json.load(f)
    f.close()

    orders = dict()
    orders['all'] = []
    orders['open'] = dict()
    orders['canceled'] = dict()
    orders['filled'] = dict()

    orders_in = 0
    orders_out = 0

    for elem in raw_orders:
        order_id = elem['order']['id']
        orders_in += 1
        if elem['event'] == 'new':
            log.info("New order for {0} {1}".format(
                elem['order']['symbol'],
                elem['order']['id'][:10]))
            orders['open'][order_id] = elem
            orders['all'].append(elem)
            orders_out += 1
            continue
        if elem['event'] == 'rejected':
            log.info("Rejected order for {0} {1}".format(
                elem['order']['symbol'],
                elem['order']['id'][:10]))
            orders['canceled'][order_id] = elem
            orders['all'].append(elem)
            orders_out += 1
            continue
        if elem['event'] == 'canceled':
            log.info("Canceled order for {0} {1}".format(
                elem['order']['symbol'],
                elem['order']['id'][:10]))
            if order_id in orders['open'].keys():
                del orders['open'][order_id]
                orders['canceled'][order_id] = elem
                orders['all'].append(elem)
                orders_out += 1
            continue
        if elem['event'] == 'fill':
            print("Filled order for {0} {1}".format(
                elem['order']['symbol'],
                elem['order']['id'][:10]))
            if order_id in orders['open'].keys():
                del orders['open'][order_id]
                orders['filled'][order_id] = elem
                orders['all'].append(elem)
                orders_out += 1
            continue
        if elem['event'] == 'replaced':
            log.info("Replaced order for {0} (replaced by: {1}) {2}".format(
                elem['order']['symbol'],
                elem['order']['replaced_by'][:10],
                elem['order']['id'][:10]))
            orders['open'][elem['order']['replaced_by']] = elem
            orders['all'].append(elem)
            orders_out += 1
            continue

    print("Orders IN  : " + str(orders_in))
    print("Orders OUT : " + str(orders_out))

    return orders


def upsert_order(conn, order):
    """
    Create a new bar into the stock_prices table
    :param conn:
    :param bar:
    :return: project id
    """
    cur = conn.cursor()

    try:
        order_tuple = (order.id, order.client_id, order.symbol, order.asset_id,
                       order.asset_class, order.status, order.side, order.order_class,
                       order.time_in_force, order.failed_at, order.filled_at, order.expired_at,
                       order.canceled_at, order.submitted_at, order.qty, order.filled_qty,
                       order.stop_price, order.limit_price, order.trail_price,
                       order.trail_percent, order.filled_avg_price, order.replaces,
                       order.replaced_by, order.replaced_at)
        cur.execute(queries.sql_upsert_into_order, order_tuple)
        if order.order_class == 'bracket' and order.legs is not None:
            for leg in order.legs:
                leg_order = Order(leg)
                upsert_order(conn, leg_order)
                cur.execute(queries.sql_insert_leg_order,
                            (order.id, leg_order.id))

    except sqlite3.IntegrityError as e:
        log.error(e)
    return cur.lastrowid


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        log.error(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


# def connect_to_account(account_type: str, provider: str):

#     conn = None

#     if not (account_type == "live" or account_type == "paper"):
#         raise ValueError("Account type can only be live or paper")

#     if not (provider == "polygon" or provider == "alpaca"):
#         raise ValueError("Provider can only be polygon or alpaca")

#     log.info("Initialising {0} data stream on {1} account".format(
#         provider,
#         account_type))
#     try:
#         if provider == "polygon" and account_type == "live":
#             conn = StreamConn(
#                 key_id=config.ALPACA_LIVE_API_KEY,
#                 secret_key=config.ALPACA_LIVE_SECRET,
#                 data_stream="polygon",
#                 debug=True)
#         elif provider == "polygon" and account_type == "paper":
#             conn = StreamConn(
#                 key_id=config.ALPACA_PAPER_API_KEY,
#                 secret_key=config.ALPACA_PAPER_SECRET,
#                 data_stream="polygon",
#                 debug=True)
#         elif provider == "alpaca" and account_type == "live":
#             conn = StreamConn(
#                 key_id=config.ALPACA_LIVE_API_KEY,
#                 secret_key=config.ALPACA_LIVE_SECRET,
#                 data_stream="alpacadatav1",
#                 debug=True)
#         else:
#             conn = StreamConn(
#                 key_id=config.ALPACA_PAPER_API_KEY,
#                 secret_key=config.ALPACA_PAPER_SECRET,
#                 data_stream="alpacadatav1",
#                 debug=True)

#     except Exception as e:
#         print(e)

#     log.info("Base URL   : " + conn._base_url)
#     log.info("Data URL   : " + conn._data_url)
#     log.info("Data Stream: " + conn._data_stream)

#     return conn

def write_order(file, order):
    file.write(str(order) + "\n")


def parse_candle(candle):
    candle = candle.replace("Agg(", "").replace(")", "").replace("'", "\"")
    try:
        candle = json.loads(candle)
        start_date_time = datetime.fromtimestamp(
            int(candle["start"]/1000),
            pytz.timezone('America/New_York')).strftime("%Y-%m-%d %H:%M:%S")
        end_date_time = datetime.fromtimestamp(
            int(candle["end"]/1000),
            pytz.timezone('America/New_York')).strftime("%Y-%m-%d %H:%M:%S")
        parsed_candle = [
            start_date_time,
            end_date_time,
            candle["open"],
            candle["high"],
            candle["low"],
            candle["close"],
            candle["volume"]
        ]
        return candle["symbol"], parsed_candle
    except:
        print(candle)
        raise ValueError("Error parsing candle {}".format(candle))


def parse_candle_file(file):

    f = open(file, "r")

    content = f.read()
    content = content.replace(")", ")@")
    candles = content.split("@")

    json_candles = dict()
    cnt = 0
    for candle in candles:
        stripped_candle = candle.strip()
        if stripped_candle != "":
            symbol, parsed_candle = parse_candle(stripped_candle)
            if symbol in json_candles:
                json_candles[symbol].append(parsed_candle)
            else:
                json_candles[symbol] = [parsed_candle]

    for key in json_candles.keys():
        print(key)

        time = []
        close = []
        for candle in json_candles[key]:
            time.append(candle[0])
            close.append(candle[5])

        assert(len(time) == len(close))
        df = pd.DataFrame({"time": [pd.to_datetime(d) for d in time], "close": close})
        #plt.scatter([pd.to_datetime(d) for d in time], df["close"],s =2)
        #df.set_index("time", inplace=True)

        plt.figure(figsize=(40, 20))
        plt.grid(b=True)
        candle_ax = plt.subplot2grid((7, 1), (0, 0), rowspan=3, colspan=1)
        candle_ax.grid(b=True)
        pct_ax = plt.subplot2grid((7, 1), (3, 0), rowspan=2, colspan=1, sharex=candle_ax)
        pct_open = plt.subplot2grid((7, 1), (5, 0), rowspan=2, colspan=1, sharex=candle_ax)

        pct_ax.grid(b=True)

        df["pct"] = df["close"].ewm(span=100).mean().diff(periods=10)
        df["pct_from_open"] = ((df["close"] - df["close"][0]) / df["close"][0]) * 100
        df["pct_from_open"].plot(ax=pct_open)
        df["pct_from_open"].rolling(window=50).mean().plot(ax=pct_open)
        
        df["close"].plot(ax=candle_ax)
        df["close"].ewm(span=100).mean().plot(ax=candle_ax)
        #plt.bar([pd.to_datetime(d) for d in time], pct_change)
        df["pct"].plot(ax=pct_ax)
        plt.grid()
        plt.show()

        plt.clf()


if __name__ == "__main__":
    # live_account = TradeApiProxy("live")
    # paper_account = TradeApiProxy("paper")

    parse_candle_file("second_candles3.txt")

    assert(False)

    # order_file = "data/orders.json"
    # orders = parse_order_file(order_file)

    # dbconn = create_connection(r"data/stock_prices.db")
    # # create tables
    # if dbconn is not None:
    #     # create projects table
    #     create_table(dbconn, queries.sql_create_second_bars_table)
    # else:
    #     log.critical("Cannot create the database connection!")
    #     exit(1)

    # conn = connect_to_account(provider="polygon", account_type="live")

    # @ conn.on(r'^trade_updates$')
    # async def on_account_updates(conn, channel, evt):
    #     order=json.loads((str(evt)
    #                         .replace("Entity(", "")
    #                         .replace(")", "")
    #                         .replace("None", "null")
    #                         .replace("False", "false")
    #                         .replace("True", "true")
    #                         .replace("'", "\"")))
    #     print('trade update :\n' + json.dumps(order, indent=4))

    #     # Storing order into an Order object
    #     # order = Order(evt)

    #     upsert_order(dbconn, Order(order))
    #     dbconn.commit()

    #     try:
    #         orders['all'].append(order)
    #         if order["status"] == 'new' or
    #            order["status"] == 'replaced' or
    #            order["status"] == 'accepted':
    #             orders['open'][order["id"]]=order
    #         elif order["status"] == 'canceled' or order["status"] == 'rejected':
    #             if order["id"] not in orders['open']:
    #                 raise ValueError(
    #                     "Trade updates handler - Order not tracked: " + order["id"])
    #             del orders['open'][order["id"]]
    #             orders['canceled'][order["id"]]=order
    #         elif order["status"] == 'fill':
    #             if order["id"] in orders['open']:
    #                 raise ValueError(
    #                     "Trade updates handler - Order not tracked: " + order["id"])
    #             del orders['open'][order["id"]]
    #             orders['filled'][order["id"]]=order
    #         else:
    #             raise ValueError(
    #                 "Trade updates handler - Uknown order status: " + order["status"])
    #     except Exception as e:
    #         print(e)

    # @ conn.on(r'^status$')
    # async def on_status(conn, channel, data):
    #     print('status update', data)

    # @ conn.on(r'^AM$')
    # async def on_minute_bars(conn, channel, bar):
    #     print('bars', bar)

    # @ conn.on(r'^A$')
    # async def on_second_bars(conn, channel, bar):
    #     print(bar)

    # # blocks forever
    # while True:
    #     try:
    #         # conn.run(['trade_updates', 'AM.AAPL,AM.TSLA'])
    #         # conn.run(['trade_updates'])
    #         conn.run(
    #             ['A.AAPL,A.FEYE,A.FB,A.MSFT,A.BABA,A.QQQ,A.ZM,A.SPY,A.ABNB,A.TM,A.T,A.APA,A.BA,A.AI,A.DKNG,A.TSLA,A.NIO,A.XOM'])
    #     finally:
    #         f = open("data/orders_new.json", "w")
    #         json.dump(orders['all'], f, indent=4)
    #         # f.write(json.dumps(orders['all'], indent=4))
    #         f.close()

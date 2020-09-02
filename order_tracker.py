import config
from api_proxy import TradeApiProxy
from alpaca_trade_api import StreamConn


class Order():
    def __init__(self, order_json):

        # Order info
        self.status = order_json.event
        self.id = order_json.order['id']
        self.type = order_json.order['type']
        self.side = order_json.order['side']
        self.order_type = order_json.order['order_type']
        self.order_class = order_json.order['order_class']
        self.time_in_force = order_json.order['time_in_force']
        self.client_order_id = order_json.order['client_order_id']

        # Asset info
        self.symbol = order_json.order['symbol']
        self.asset_id = order_json.order['asset_id']
        self.asset_class = order_json.order['asset_class']

        # Timing
        self.failed_at = order_json.order['failed_at']
        self.filled_at = order_json.order['filled_at']
        self.expired_at = order_json.order['expired_at']
        self.canceled_at = order_json.order['canceled_at']
        self.submitted_at = order_json.order['submitted_at']
        self.extended_hours = order_json.order['extended_hours']

        # Price info
        self.qty = order_json.order['qty']
        self.filled_qty = order_json.order['filled_qty']
        self.stop_price = order_json.order['stop_price']
        self.limit_price = order_json.order['limit_price']
        self.trail_price = order_json.order['trail_price']
        self.trail_percent = order_json.order['trail_percent']
        self.filled_avg_price = order_json.order['filled_avg_price']

        # Other orders
        self.replaces = order_json.order['replaces']
        self.replaced_by = order_json.order['replaced_by']
        self.replaced_at = order_json.order['replaced_at']

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


def connect_to_account(account_type: str, provider: str):

    conn = None

    if not (account_type == "live" or account_type == "paper"):
        raise ValueError("Account type can only be live or paper")

    if not (provider == "polygon" or provider == "alpaca"):
        raise ValueError("Provider can only be polygon or alpaca")

    print("Initialising " + provider +
          " data stream on " + account_type + " account")
    try:
        if provider == "polygon" and account_type == "live":
            conn = StreamConn(
                key_id=config.ALPACA_LIVE_API_KEY,
                secret_key=config.ALPACA_LIVE_SECRET,
                data_stream="polygon",
                debug=True)
        elif provider == "polygon" and account_type == "paper":
            conn = StreamConn(
                key_id=config.ALPACA_PAPER_API_KEY,
                secret_key=config.ALPACA_PAPER_SECRET,
                data_stream="polygon",
                debug=True)
        elif provider == "alpaca" and account_type == "live":
            conn = StreamConn(
                key_id=config.ALPACA_LIVE_API_KEY,
                secret_key=config.ALPACA_LIVE_SECRET,
                data_stream="alpacadatav1",
                debug=True)
        else:
            conn = StreamConn(
                key_id=config.ALPACA_PAPER_API_KEY,
                secret_key=config.ALPACA_PAPER_SECRET,
                data_stream="alpacadatav1",
                debug=True)

    except Exception as e:
        print(e)

    print("Base URL   : " + conn._base_url)
    print("Data URL   : " + conn._data_url)
    print("Data Stream: " + conn._data_stream)

    return conn


def write_order(file, order):
    file.write(str(order) + "\n")


if __name__ == "__main__":
    #live_account = TradeApiProxy("live")
    #paper_account = TradeApiProxy("paper")

    order_file = open('data/orders.dat', 'a')
    open_orders = dict()
    closed_orders = dict()
    conn = connect_to_account(provider="polygon", account_type="live")

    @conn.on(r'^trade_updates$')
    async def on_account_updates(conn, channel, evt):
        print('trade update', evt)
        order = Order(evt)

        if order.status == 'new':
            open_orders[order.id] = order
        elif order.status == 'canceled' or order.status == 'fill':
            if order.id in open_orders:
                del open_orders[order.id]
            closed_orders[order.id] = order
        else:
            print("Unknown order status: " + order.status)

        write_order(order_file, evt)

    @conn.on(r'^status$')
    async def on_status(conn, channel, data):
        print('status update', data)

    @conn.on(r'^AM$')
    async def on_minute_bars(conn, channel, bar):
        print('bars', bar)

    @conn.on(r'^A$')
    async def on_second_bars(conn, channel, bar):
        print('bars', bar)

    # blocks forever
    try:
        #conn.run(['trade_updates', 'AM.AAPL,AM.TSLA'])
        conn.run(['trade_updates'])
    finally:
        order_file.close()

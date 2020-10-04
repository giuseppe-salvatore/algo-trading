import conf.secret as config
import alpaca_trade_api as alpaca

from lib.util.logger import log

STOP_LOSS_PERC = 0.5
open_orders = None
close_orders = None
all_orders = None
open_orders_dic = dict()




class AlpacaTrading():

    def __init__(self, account_type: str = "paper"):
        '''
        Instanciating a TradeApiProxy will provide authentication and you will
        be ready to use the object's functions
        '''
        self.api = None
        self.account_type = account_type
        self.authenticate()
        self._cached_watchlist = None

    def authenticate(self):
        '''
        By default this will open a connection to the pater trading endpoint
        so no real money will be used for your transactions. To use a founded
        account and real money use conf.secret.ALPACA_REAL_TRADING_REST_ENDPOINT
        insead of conf.secret.ALPACA_PAPER_TRADING_REST_ENDPOINT
        '''

        if not (self.account_type == 'paper' or
                self.account_type == 'paper2' or
                self.account_type == 'live'):
            raise ValueError(
                "Account type should be either 'paper', 'paper2' or 'live': " + self.account_type + " provided instead")

        log.info("Initialising Alpaca REST API to trade with " + self.account_type + " account")

        if self.account_type == 'live':
            log.warn("Using live account, carefull as you are using real money here!!!")
            alpaca_api_key = config.ALPACA_LIVE_API_KEY
            alpaca_secret = config.ALPACA_LIVE_SECRET
            alpaca_api_endpoint = config.ALPACA_LIVE_TRADING_REST_ENDPOINT
        elif self.account_type == 'paper':
            alpaca_api_key = config.ALPACA_PAPER_API_KEY
            alpaca_secret = config.ALPACA_PAPER_SECRET
            alpaca_api_endpoint = config.ALPACA_PAPER_TRADING_REST_ENDPOINT
        else:
            assert(self.account_type == 'paper2')
            alpaca_api_key = config.ALPACA_PAPER_API_KEY_2
            alpaca_secret = config.ALPACA_PAPER_SECRET_2
            alpaca_api_endpoint = config.ALPACA_PAPER_TRADING_REST_ENDPOINT

        # Make sure you set your API key and secret in the config module
        self.api = alpaca.REST(
            alpaca_api_key,
            alpaca_secret,
            alpaca_api_endpoint,
            api_version='v2'
        )

        log.info("Alpaca REST API " + self.account_type + " account successfully initialised")
        

    def can_trade(self):
        '''
        As a first rule always check we can trade when we need to, especially before entering
        long positions
        '''
        account = self.api.get_account()
        if account.trading_blocked:
            return False
        return True

    def get_equity_value(self):
        account = self.api.get_account()
        return float(account.last_equity)

    def get_minute_barset(self, ticker: str):
        return self.api.get_barset(ticker, 'minute', limit=1000)

    def get_5_minutes_barset(self, ticker):
        return self.api.get_barset(ticker, '5Min', limit=1000)

    def get_limit_5_minutes_barset(self, ticker, limit):
        return self.api.get_barset(ticker, '5Min', limit=limit)

    def get_limit_minute_barset(self, ticker: str, limit):
        return self.api.get_barset(ticker, 'minute', limit=limit)

    def get_quote(self, ticker):
        return self.api.get_last_quote(ticker)

    def get_positions(self):
        return self.api.list_positions()

    def update_stop_loss_order_for(self, pos):
        if open_orders is not None:
            self.list_open_orders()
            for order in open_orders:
                if order.symbol == pos.symbol:
                    self.update_stop_loss_order(
                        order.id, pos.market_value, pos.qty, pos.side)

    def check_and_update_stop_loss_orders(self):
        positions = self.get_positions()
        open_orders = self.list_open_orders()

        print("{:>6s}, {:>3s}, {:>5s}, {:>10s}, {:>10s}".format(
            "symbol",
            "qty",
            "side",
            "stop price",
            "limit price"
        ))
        for pos in positions:
            found = False
            for ord in open_orders:
                if ord.symbol == pos.symbol:
                    found = True
                    break
            if not found:
                # print("No stop loss for " + pos.symbol + " placing one now")
                self.cover_position_with_stop_loss(pos)

    def update_stop_loss_order(self, id: str, market_val: str, qty: str, pos_side: str):
        side = 'sell' if pos_side == 'long' else 'buy'
        stock_market_val = float(market_val) / float(qty)
        stop = stock_market_val * \
            (1.0 - STOP_LOSS_PERC / 100.0) if side == 'sell' else stock_market_val * \
            (1.0 + STOP_LOSS_PERC / 100.0)
        self.replace_limit_stop_order_by_id(id, stop)

    def has_open_order(self, symbol: str):
        self.list_open_orders(use_cache=True)
        for order in open_orders:
            if order.symbol == symbol:
                return True
        return False

    def cover_position_with_stop_loss(self, pos):

        if self.has_open_order(pos.symbol):
            print("Stock " + pos.symbol + " is already covered by order")
            return
        side = 'sell' if pos.side == 'long' else 'buy'
        market_val = float(pos.market_value) / int(pos.qty)
        stop = market_val * \
            (1.0 - STOP_LOSS_PERC / 100.0) if side == 'sell' else market_val * \
            (1.0 + STOP_LOSS_PERC / 100.0)
        limit = market_val * \
            (1.0 - STOP_LOSS_PERC / 150000.0) if side == 'sell' else market_val * \
            (1.0 + STOP_LOSS_PERC / 150000.0)

        self.submit_stop_loss_order(
            symbol=pos.symbol,
            side=side,
            stop=stop,
            limit=limit,
            qty=pos.qty)

    def scale_trading(self, symbol: str, stop_loss_perc: float):
        pass

    def list_new_orders(self):
        orders = self.api.list_orders()
        new_orders = list()
        for order in orders:
            if order.status == 'new' or \
               order.status == 'replaced':
                new_orders.append(order)
        return new_orders

    def list_all_orders(self, use_cache: bool = True):
        global all_orders
        if not (use_cache and all_orders is not None):
            all_orders = self.api.list_orders(status='all', limit=500)

        return all_orders

    def list_open_orders(self, use_cache: bool = True):
        global open_orders
        if not (use_cache and open_orders is not None):
            open_orders = self.api.list_orders(status='open', limit=500)

        return open_orders

    def list_closed_orders(self, use_cache: bool = True):
        global closed_orders
        if not (use_cache and closed_orders is not None):
            closed_orders = self.api.list_orders(status='closed', limit=500)

        return closed_orders

    def replace_order(self, id: str, qty: int = None, limit: float = None, stop: float = None, tif: str = None):
        stop = "{:.2f}".format(stop) if stop is not None else None
        limit = "{:.2f}".format(limit) if limit is not None else None
        qty = str(qty) if qty is not None else None
        self.api.replace_order(
            id,
            qty=qty,
            limit_price=limit,
            stop_price=stop,
            time_in_force=tif
        )

    def replace_limit_stop_order_by_id(self, id: str, stop: float, limit: float = None):
        self.replace_order(
            id=id,
            stop=stop)

    def replace_limit_stop_order(self, symbol: str, stop: float, limit: float):
        open_orders = self.list_open_orders()
        for order in open_orders:
            if symbol in order.symbol:
                self.replace_order(
                    order.id,
                    limit,
                    stop)

    def submit_braket_order(self, symbol: str, limit_target: float, stop: float, limit: float):
        pass

    def submit_stop_loss_order(self, symbol: str, side: str, qty: int, stop: float, limit: float):
        stop_str = "{:.2f}".format(stop) if stop is not None else None
        limit_str = "{:.2f}".format(limit) if limit is not None else None
        qty = str(abs(int(qty)))
        print("{:>6s}, {:>3s}, {:>5s}, {:>10s}, {:>10s}".format(
            symbol,
            qty,
            side,
            stop_str,
            limit_str
        ))
        self.api.submit_order(
            symbol=symbol,
            type='stop',
            qty=qty,
            side=side,
            stop_price=stop_str,
            limit_price=None,
            time_in_force='gtc'
        )

    def fetch_watchlist(self):
        watch_lists = self.api.get_watchlists()
        self._cached_watchlist = dict()
        self._cached_watchlist_id = watch_lists[0].id
        self._cached_watchlist[self._cached_watchlist_id] = self.api.get_watchlist(
            self._cached_watchlist_id).assets
        return self._cached_watchlist[self._cached_watchlist_id]

    def delete_watchlist(self):
        pass

    def create_watchlist(self):
        pass

    def add_symbol_to_watchlist(self, symbol: str):
        if self._cached_watchlist is None:
            self.fetch_watchlist()

        try:
            self.api.add_to_watchlist(self._cached_watchlist_id, symbol)
        except Exception as e:
            print("WARNING: Problem adding " + symbol + " " + str(e))

    def get_watchlist(self):
        if self._cached_watchlist is None:
            self.fetch_watchlist()

        watchlist_symbols = list()
        wl = None
        for wl in self._cached_watchlist:
            for elem in self._cached_watchlist[wl]:
                #self.api.delete_from_watchlist(wl, elem['symbol'])
                watchlist_symbols.append(elem['symbol'])

        return watchlist_symbols

    def sort_watchlist(self):
        watchlist_symbols = self.get_watchlist()
        watchlist_symbols.sort()

        for stock in watchlist_symbols:
            self.add_symbol_to_watchlist(stock)

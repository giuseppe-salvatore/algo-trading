import config
import alpaca_trade_api



class TradeApiProxy():

    def __init__(self):
        '''
        Instanciating a TradeApiProxy will provide authentication and you will
        be ready to use the object's functions
        '''
        self.api = None
        self.authenticate()

    def authenticate(self):
        '''
        By default this will open a connection to the pater trading endpoint
        so no real money will be used for your transactions. To use a founded
        account and real money use config.ALPACA_REAL_TRADING_REST_ENDPOINT
        insead of config.ALPACA_PAPER_TRADING_REST_ENDPOINT
        '''

        # Make sure you set your API key and secret in the config module     
        self.api = alpaca_trade_api.REST(
            config.ALPACA_API_KEY,
            config.ALPACA_SECRET,
            config.ALPACA_PAPER_TRADING_REST_ENDPOINT,
            api_version='v2'
        )

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


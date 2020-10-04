import json

investments_data_file = open("data/investments.json", "r")
stocks_portfolio = json.load(investments_data_file)

def get_total_capital_invested():
    total_capital_invested = 0.0
    
    for stock in stocks_portfolio:
        total_capital_invested += get_capital_invested_in(stock)
    
    return total_capital_invested

def get_shares_for(symbol):
    shares = 0.0

    if symbol in stocks_portfolio:
        for investment in stocks_portfolio[symbol]["investments"]:
            shares += investment["shares"]

    return shares


def get_capital_gain_for(symbol, real_time_value):
    instant_gain = 0.0

    if real_time_value == 0.0:
        return instant_gain

    if symbol in stocks_portfolio:
        instant_gain = ((real_time_value * get_shares_for(symbol)) -
                        get_capital_invested_in(symbol))
        stocks_portfolio[symbol]["gain"] = instant_gain

    return instant_gain


def get_latest_recorded_gain_for(symbol):
    latest_gain = 0.0

    if symbol in stocks_portfolio:
        latest_gain = stocks_portfolio[symbol]["gain"]
    
    return latest_gain


def get_total_capital_gain():
    total_gain = 0.0
    
    for symbol in stocks_portfolio:
        total_gain += get_latest_recorded_gain_for(symbol)
    
    return total_gain


def get_portfolio_stocks():
    return stocks_portfolio.keys()

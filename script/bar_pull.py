import sqlite3
import datetime
import pandas as pd
import lib.util.logger as log
import lib.db.queries as db_queries
import pandas_market_calendars as mcal
import strategies.scalping.recommended_stocks
from sqlite3 import Error
from lib.trading.alpaca import AlpacaTrading


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
        log.error(e)


def insert_bar(conn, price):
    """
    Create a new bar into the minute_bars table
    :param conn:
    :param bar:
    :return: project id
    """
    sql = ''' INSERT INTO minute_bars(symbol,time,open,close,high,low,volume)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, price)
    except sqlite3.IntegrityError as e:
        log.error(e)
    return cur.lastrowid


def get_minute_bars_in_timeframe(account, db_conn, symbol, time_from, time_to):
    """
    Query all rows in the minute_bars table
    :param conn: the Connection object
    :return:
    """

    nyse = mcal.get_calendar('NYSE')
    nsye_dates = nyse.schedule(start_date=time_from, end_date=time_to)
    print(nsye_dates)
    expected_bar_count = 390 * len(nsye_dates.index)

    # Following block was using pure SQL but alternatively we can use pandas sql reader
    #
    # cur = conn.cursor()
    # cur.execute("SELECT * FROM stock_prices WHERE symbol = \'" +
    #             symbol + "\' AND (time BETWEEN \'" + time_from + "\' AND \'" + time_to + "\')")
    # rows = cur.fetchall()

    df = pd.read_sql("SELECT time, open, close, low, high, volume FROM minute_bars WHERE symbol=\'" + symbol +
                     "\' AND (time BETWEEN \'" + time_from + "\' AND \'" + time_to + "\')", db_conn, index_col='time')

    print("Expected bar count = " + str(expected_bar_count))
    print("Available bar count = " + str(len(df)))
    if len(df) < expected_bar_count:
        msg = "Missing data, fetching from data provider API (expected: "
        msg += str(expected_bar_count) + " got: " + str(len(df)) + ")"
        log.warn(msg)

        for day in nsye_dates.index:
            print("Retreiving data for day " + str(day))
            data = fetch_stock_data(account, symbol, str(
                day)[:10], str(day+datetime.timedelta(days=1))[:10])
            print("Retreived " + str(len(data)))
            if len(data) < 390:
                log.warning(str(390 - len(data)) + " bars missing on " + str(day))
            for elem in data:
                insert_bar(db_conn, (symbol, str(elem.timestamp)[
                    :19], elem.open, elem.close, elem.high, elem.low, elem.volume))
        db_conn.commit()

        # Following block was using pure SQL but alternatively we can use pandas sql reader
        #
        # cur = conn.cursor()
        # cur.execute("SELECT * FROM stock_prices WHERE symbol = \'" +
        #     symbol + "\' AND (time BETWEEN \'" + time_from + "\' AND \'" + time_to + "\')")
        # rows = cur.fetchall()
        sql = "SELECT time, open, close, low, high, volume "
        sql += "FROM minute_bars "
        sql += "WHERE symbol=\'" + symbol + "\' "
        sql += "AND (time BETWEEN \'" + time_from + "\' AND \'" + time_to + "\')"
        df = pd.read_sql(sql, db_conn, index_col='time')

    if len(df) < expected_bar_count:
        print("WARNING: bars missing")

    return df


def fetch_stock_data(account, symbol, date_from, date_to):
    return account.api.get_aggs(
        symbol,
        timespan='minute',
        _from=date_from,
        to=date_to, multiplier=1)


if __name__ == "__main__":

    live_account = AlpacaTrading("live")
    db_conn = create_connection(r"data/stock_prices.db")
    # create tables
    if db_conn is not None:
        # create projects table
        create_table(db_conn, db_queries.sql_create_minute_bars_table)
    else:
        print("Error! cannot create the database connection.")

    # barset = live_account.get_limit_minute_barset('AAPL,TSLA', limit=100)

    stocks = strategies.scalping.recommended_stocks.stocks

    # barset = live_account.api.get_aggs('QQQ', timespan='minute', _
    # from='2019-04-15', to='2019-04-16', multiplier=1)
    # for symbol in stocks:
    #     print("Fetching " + symbol + " stock prices")
    #     barset = fetch_stock_data(live_account, symbol, '2019-04-15', '2019-04-16')
    #     print("Storing " + symbol + " stock prices")
    #     for elem in barset:
    #         insert_bar(conn, (symbol, str(elem.timestamp)[:19], elem.open,
    #                     elem.close, elem.high, elem.low, elem.volume))
    #     conn.commit()

    symbol = 'AAPL'
    df = get_minute_bars_in_timeframe(
        live_account, db_conn, symbol, '2020-05-08', '2020-08-26')
    print(df)

    # print(mcal.get_calendar_names())

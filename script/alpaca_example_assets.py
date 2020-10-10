import sys
import time
import sqlite3
import datetime
import api_proxy
import db_queries

import market_data_provider.finnhub_proxy
import market_data_provider.polygon_proxy as polygon_data
from sqlite3 import Error
from lib.util.logger import log

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


def insert_asset(conn, asset, date):
    """
    Create a new bar into the tradable_assets table
    :param conn:
    :param bar:
    :return: project id
    """
    sql = ''' INSERT INTO tradable_assets(id,symbol,name,type,exchange,date,shortable,marginable)
              VALUES(?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    asset_tuple = (asset.id, asset.symbol, asset.name, asset._raw['class'], asset.exchange, str(
        date)[:10], asset.shortable, asset.marginable)
    try:
        cur.execute(sql, asset_tuple)
    except sqlite3.IntegrityError as e:
        log.error(e)
    return cur.lastrowid


def insert_bar(conn, bar):
    """
    Create a new bar into the minute_bars table
    :param conn:
    :param bar:
    :return: project id
    """
    sql = ''' INSERT INTO minute_bars(symbol,time,open,high,low,close,volume)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, bar)
    except sqlite3.IntegrityError as e:
        log.error(e)
    return cur.lastrowid

def get_filtered_watchlist(conn):
    cur = db_conn.cursor()
    cur.execute("SELECT * FROM filtered_watchlist;")
    return cur.fetchall()

def update_asset_with_company_info(conn, symbol, params):
    sql = ''' UPDATE tradable_assets
              SET market_cap = ? ,
                  industry = ? ,
                  sector = ? ,
                  stock_type = ? ,
                  url = ? ,
                  logo_url = ? ,
                  description = ?
              WHERE symbol = ?'''
    cur = conn.cursor()
    cur.execute("BEGIN")
    try:
        cur.execute(sql, (
            params["marketcap"],
            params["industry"],
            params["sector"],
            params["type"],
            params["url"],
            params["logo"],
            params["description"],
            symbol))
        cur.execute("COMMIT")
    except Exception as e:
        log.error(e)
        cur.execute("ROLLBACK")

def get_tradable_asset_symbols(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT symbol FROM tradable_assets ORDER BY symbol;")
    rows = cur.fetchall()
    assets = []
    for row in rows:
        assets.append(row[0])
    return assets

def get_watchlist(db_conn):
    cur = db_conn.cursor()
    cur.execute("SELECT symbol FROM watchlist ORDER BY symbol;")
    rows = cur.fetchall()
    watchlist = []
    for row in rows:
        watchlist.append(row[0])
    return watchlist

def inset_all_into_watchlist(conn, symbols):

    wl = get_watchlist(conn)
    print(wl)
    for elem in wl:
        if elem in symbols:
            print("WARNING: " + elem + " already in watchlist")
            symbols.remove(elem)

    if len(symbols) == 0:
        print("WARNING: no symbols to add")
        return None

    conn.isolation_level = None
    cur = conn.cursor()

    cur.execute("BEGIN")

    for symbol in symbols:
        try:
            sql = '''INSERT INTO watchlist(symbol) VALUES(?)'''
            cur.execute(sql, (symbol,))
        except sqlite3.IntegrityError as error:
            print(error)
            cur.execute("ROLLBACK")
            return

    cur.execute("COMMIT")


def insert_symbol_in_watchlist(conn, symbol):
    """
    Create a new bar into the watchlist table
    :param conn:
    :param symbol:
    :return: project id
    """
    sql = ''' INSERT INTO watchlist(symbol)
              VALUES(?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (symbol,))
    except sqlite3.IntegrityError as error:
        print(error)
    return cur.lastrowid

def update_symbol(db_conn, symbol):
    params = polygon_data.get_company_details(symbol)
    update_asset_with_company_info(db_conn, symbol, params)


if __name__ == "__main__":

    paper_account = api_proxy.TradeApiProxy("paper")
    assets = paper_account.api.list_assets()

    db_conn = create_connection(r"data/stock_prices.db")
    # create tables
    if db_conn is not None:
        # create projects table
        create_table(
            db_conn, db_queries.sql_create_table_tradable_assets_table)
    else:
        print("Error! cannot create the database connection.")
    db_conn.commit()

    #
    # This will insert new symbols in the simple watchlist
    #
    watchlist = paper_account.get_watchlist()
    inset_all_into_watchlist(db_conn, watchlist)

    # assets = get_tradable_asset_symbols(db_conn)

    # skip = True
    # for symbol in assets:

    #     if symbol == "LSAF":
    #         skip = False

    #     if skip:
    #         print("Skipping " + symbol)
    #         continue

    #     print("Fetching data for " + symbol, end="")
    #     try:
    #         update_symbol(db_conn, symbol)
    #         time.sleep(1)
    #         print(" DONE")
    #     except Exception as e:
    #         print(" ERROR " + str(e))

    # time.sleep(120)

    sys.exit(0)

    count = 0
    by_exchange = dict()
    date = datetime.datetime.now()
    for asset in assets:
        if asset.exchange in by_exchange:
            by_exchange[asset.exchange].append(asset)
        else:
            by_exchange[asset.exchange] = [asset]
        # if asset.tradable == True:
        #     insert_asset(db_conn, asset, date)
    # db_conn.commit()

    for ex in by_exchange:
        print(ex + " " + str(len(by_exchange[ex])))

    cur = db_conn.cursor()
    cur.execute("SELECT symbol FROM tradable_assets ")
    rows = cur.fetchall()

    start_from = "LFUS"
    skip = True
    for row in rows:
        symbol = row[0]
        try:
            if symbol == start_from:
                skip = False
            if skip:
                log.info("Skipping symbol " + symbol, end="")
                continue

            log.info("Processing symbol " + symbol, end="")
            log.info("  Fetching", end="")
            result = market_data_provider.finnhub_proxy.get_minute_bars(
                symbol, "2019-09-27", "2019-09-28")
            time.sleep(15)
            if result is None:
                log.info("  Symbol not available or no data", end="")
                continue
            log.info("  (market=" + str(result["market"]) + ")", end="")
            log.info("  (extra=" + str(result["extra_hours"]) + ")", end="")
            if result["market"] < 385:
                log.info("  Not enough market data", end="")
                continue
            for elem in result['data']:
                insert_bar(db_conn, elem)
            log.info("  Committing", end="")
            db_conn.commit()
            insert_symbol_in_watchlist(db_conn, symbol)
            db_conn.commit()
            log.info("  Done", end="")
        except Exception as e:
            log.error("Error parsing symbol " + symbol)
            log.error(e)
            time.sleep(10)
        finally:
            print("")

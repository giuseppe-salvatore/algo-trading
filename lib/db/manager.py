import os
import re
import sqlite3
import pandas as pd
import lib.db.queries as query

from sqlite3 import Error
from datetime import datetime
from datetime import timedelta
from lib.util.logger import log

DATETIME_FORMAT_DATE_ONLY = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
DATETIME_FORMAT_FULL = "%Y-%m-%d %H:%M:%S"


class DBManager:
    def __init__(self):
        db_file = os.environ.get("SQLITE_DB_FILE")
        cwd = os.getcwd()
        log.debug("Working directory: " + cwd)
        if not cwd.endswith("algo-trading"):
            log.info(re.sub("algo-trading.*", "algo-trading", cwd))
            os.chdir(re.sub("algo-trading.*", "algo-trading", cwd))
            log.debug("Changing Current Working directory to: " + os.getcwd())

        if db_file is None:
            log.warning(
                "Expected SQLITE_DB_FILE varialbe to be set pointing to the db file to use"
            )
            db_file = "data/stock_prices.db"
            log.warning("Setting the db file to local file: {}".format(db_file))
        else:
            log.debug("SQLITE_DB_FILE = {}".format(db_file))

        if not os.path.exists(db_file):
            log.fatal("Database file doesn't exist: {}".format(db_file))
        else:
            log.debug("Found database file: {}".format(db_file))

        self.conn = self._create_connection(db_file)

    def _create_connection(self, db_file):
        """create a database connection to a SQLite database"""
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            log.fatal(e)

    def close(self):
        self.conn.close()

    def create_table(self, query):
        """create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(query)
        except Error as e:
            log.error(e)

    def delete_rows_from(self, table, where_condition):
        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM " + table + " WHERE " + where_condition)
            self.conn.commit()
        except Error as e:
            log.error(e)

    def minute_candles_to_dataframe(
        self, symbol: str, start_date: datetime, end_date: datetime
    ):
        query = "SELECT time AS datetime, open, close, low, high, volume "
        query += "FROM minute_bars "
        query += "WHERE symbol='{}' AND (time BETWEEN '{}' AND '{}')".format(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        )
        log.debug(query)
        df = pd.read_sql(query, self.conn, index_col="datetime")
        df.index = pd.to_datetime(df.index, format="%Y-%m-%d %H:%M", exact=False)
        return df

    def get_all_minute_candles_to_dataframe(
        self, symbol: str, from_table="minute_bars"
    ):
        query = """SELECT time AS datetime, open, close, low, high, volume
                FROM {}
                WHERE symbol='{}'""".format(
            from_table, symbol
        )
        log.debug(query)
        df = pd.read_sql(query, self.conn, index_col="datetime")
        df.index = pd.to_datetime(df.index, format=DATETIME_FORMAT, exact=False)
        return df

    def get_filtered_watchlist(self):
        cur = self.conn.cursor()
        cur.execute("SELECT symbol FROM filtered_watchlist")
        return cur.fetchall()

    def get_all_symbols(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT symbol FROM minute_bars")
        return cur.fetchall()

    def get_all_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'"
        )
        return cur.fetchall()

    def get_filtered_watchlist_sortedby_marketcap(self):
        cur = self.conn.cursor()
        cur.execute(query.sql_get_watchlist_by_market_cap)
        return cur.fetchall()

    def get_diff_dataframe(self, symbol: str, dataframe_to_store: pd.DataFrame):
        start_datetime = pd.to_datetime(dataframe_to_store.iloc[[0]].index[0])
        end_datetime = pd.to_datetime(dataframe_to_store.iloc[[-1]].index[0])
        dataframe_in_db = self.minute_candles_to_dataframe(
            symbol, start_datetime, end_datetime
        )
        # log.warning("----------------------> Dataframe to store\n{}".format(dataframe_to_store))

        # log.warning("Dataframe in DB\n{}".format(dataframe_in_db))
        if len(dataframe_in_db) > 0:
            # Unfortunately we need both reset_index() and set_index('datetime') to keep
            # the datetime index in the resulting db
            result_df = (
                dataframe_to_store.reset_index()
                .merge(dataframe_in_db, how="outer", indicator=True)
                .loc[lambda x: x["_merge"] == "left_only"]
                .set_index("datetime")
            )
            result_df.drop(columns=["_merge"], inplace=True)
            # log.warning("Dataframe to merge\n{}".format(result_df))
            return result_df
        return dataframe_to_store

    def dataframe_to_minute_candles(self, symbol: str, dataframe: pd.DataFrame):
        dataframe["symbol"] = symbol
        diff_dataframe_to_store = self.get_diff_dataframe(symbol, dataframe)

        diff_dataframe_to_store.to_sql(
            "minute_bars", self.conn, if_exists="append", index=True, index_label="time"
        )
        self.conn.commit()

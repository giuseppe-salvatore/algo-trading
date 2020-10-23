import os
import sqlite3
import pandas as pd
from sqlite3 import Error
from datetime import datetime
from lib.util.logger import log


class DBManager():

    def __init__(self):
        db_file = os.environ.get("SQLITE_DB_FILE")
        log.debug("Working directory: " + os.getcwd())
        if db_file is None:
            log.warning("Expected SQLITE_DB_FILE varialbe to be set pointing to the db file to use")
            db_file = "data/stock_prices.db"
            log.warning("Setting the db file to local file: {}".format(db_file))
        else:
            log.debug("SQLITE_DB_FILE = {}".format(db_file))

        if not os.path.exists(db_file):
            log.fatal("Database file doesn't exist: {}".format(db_file))
        else:
            log.info("Found database file: {}".format(db_file))

        self.conn = self._create_connection(db_file)

    def _create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            log.fatal(e)

    def close(self):
        self.conn.close()

    def create_table(self, query):
        """ create a table from the create_table_sql statement
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

    def minute_candles_to_dataframe(self,
                                    symbol: str,
                                    start_date: datetime,
                                    end_date: datetime):
        query = "SELECT time AS datetime, open, close, low, high, volume "
        query += "FROM minute_bars "
        query += "WHERE symbol='{}' AND (time BETWEEN '{}' AND '{}')".format(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        log.debug(query)
        df = pd.read_sql(query, self.conn, index_col='datetime')
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M', exact=False)
        return df

    def dataframe_to_minute_candles(self, symbol: str, dataframe: pd.DataFrame):
        dataframe['symbol'] = symbol
        # print(dataframe)

        dataframe.to_sql(
            "minute_bars",
            self.conn,
            if_exists='append',
            index=True,
            index_label='time')
        self.conn.commit()

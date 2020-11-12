sql_create_order_table = """CREATE TABLE IF NOT EXISTS orders (
                                    id              VARCHAR(20) PRIMARY KEY,
                                    client_id       VARCHAR(6) NOT NULL,
                                    symbol          VARCHAR(6) NOT NULL,
                                    asset_id        VARCHAR(20) NOT NULL,
                                    asset_class     VARCHAR(10) NOT NULL,
                                    status          VARCHAR(20) NOT NULL,
                                    side            VARCHAR(10) NOT NULL,
                                    order_class     VARCHAR(10) NOT NULL,
                                    time_in_force   DATETIME NOT NULL,
                                    failed_at       DATETIME,
                                    filled_at       DATETIME,
                                    expired_at      DATETIME,
                                    canceled_at     DATETIME,
                                    submitted_at    DATETIME,
                                    qty             INTEGER NOT NULL,
                                    filled_qty      INTEGER,
                                    stop_price      REAL,
                                    limit_price     REAL,
                                    trail_price     REAL,
                                    trail_percent   REAL,
                                    filled_avg_price REAL,
                                    replaces        VARCHAR(20),
                                    replaced_by     VARCHAR(20),
                                    replaced_at VA  RCHAR(20)
                                );"""


sql_create_order_legs_table = """CREATE TABLE IF NOT EXISTS order_legs (
                                    id           INTEGER PRIMARY KEY,
                                    order_id     VARCHAR(20) NOT NULL,
                                    order_leg_id VARCHAR(20) NOT NULL,
                                    UNIQUE(order_id, order_leg_id)
                                );"""


sql_create_minute_bars_table = """CREATE TABLE IF NOT EXISTS minute_bars (
                                    id      INTEGER PRIMARY KEY,
                                    symbol  VARCHAR(6),
                                    time    DATETIME NOT NULL,
                                    open    REAL NOT NULL,
                                    close   REAL NOT NULL,
                                    high    REAL NOT NULL,
                                    low     REAL NOT NULL,
                                    volume  REAL NOT NULL,
                                    UNIQUE (symbol, time)
                                );"""

sql_create_data_provider_table = """CREATE TABLE IF NOT EXISTS market_data_providers (
                                    id      INTEGER      PRIMARY KEY,
                                    name    VARCHAR (15) UNIQUE NOT NULL,
                                    website VARCHAR (40) UNIQUE NOT NULL
                                    );"""

sql_create_trading_platforms_table = """CREATE TABLE IF NOT EXISTS trading_platforms (
                                    id   INTEGER      PRIMARY KEY NOT NULL,
                                    name VARCHAR (20) UNIQUE NOT NULL
                                    );"""

sql_create_table_tradable_assets_table = """CREATE TABLE IF NOT EXISTS tradable_assets (
                                    id         STRING   PRIMARY KEY NOT NULL,
                                    symbol     CHAR (8) NOT NULL,
                                    name       STRING   NOT NULL,
                                    type       STRING   NOT NULL,
                                    exchange   STRING   NOT NULL,
                                    date       DATE     NOT NULL,
                                    shortable  BOOLEAN  NOT NULL,
                                    marginable BOOLEAN  NOT NULL,
                                    UNIQUE (symbol,date)
                                );"""

sql_upsert_into_order = """ INSERT INTO orders(
    id,client_id,
    symbol,
    asset_id,
    asset_class,
    status,
    side,
    order_class,
    time_in_force,
    failed_at,
    filled_at,
    expired_at,
    canceled_at,
    submitted_at,
    qty,
    filled_qty,
    stop_price,
    limit_price,
    trail_price,
    trail_percent,
    filled_avg_price,
    replaces,
    replaced_by,
    replaced_at)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET
        status=excluded.status,
        time_in_force=excluded.time_in_force,
        failed_at=excluded.failed_at,
        filled_at=excluded.filled_at,
        expired_at=excluded.expired_at,
        canceled_at=excluded.canceled_at,
        submitted_at=excluded.submitted_at,
        qty=excluded.qty,
        filled_qty=excluded.filled_qty,
        stop_price=excluded.stop_price,
        limit_price=excluded.limit_price,
        trail_price=excluded.trail_price,
        trail_percent=excluded.trail_percent,
        filled_avg_price=excluded.filled_avg_price,
        replaces=excluded.replaces,
        replaced_by=excluded.replaced_by,
        replaced_at=excluded.replaced_at; """

sql_insert_leg_order = """INSERT INTO order_legs(
    order_id ,
    order_leg_id)
    VALUES(?,?);"""

sql_get_watchlist_by_market_cap = """SELECT symbol
                                     FROM filtered_watchlist
                                     WHERE market_cap > 4000000000
                                     ORDER BY market_cap DESC"""

sql_get_minute_candles = """SELECT time, open, close, high, low, volume
                            FROM minute_bars
                            WHERE symbol = '?' AND time > ? AND time < ?"""

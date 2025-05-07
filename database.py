# ib_trade_engine/database.py
import sqlite3
from pathlib import Path
import pandas as pd

SCHEMA = """
CREATE TABLE IF NOT EXISTS qty_runs (
    run_ts TEXT,
    symbol TEXT,
    notional REAL,
    side TEXT,
    base_ccy TEXT,
    bid REAL,
    ask REAL,
    last REAL,
    fx REAL,
    last_base REAL,
    shares INTEGER
);
"""

def init_db(db_path: str | Path):
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn

def dump(df: pd.DataFrame, conn: sqlite3.Connection):
    df.to_sql("qty_runs", conn, if_exists="append", index=False)

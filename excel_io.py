# ib_trade_engine/excel_io.py
from __future__ import annotations
import pandas as pd
import xlwings as xw


def read_orders(book_path: str, sheet: str) -> pd.DataFrame:
    """Return a DF with lower‑case column names, dropping completely blank rows."""
    with xw.App(visible=False) as app:
        book = app.books.open(book_path)
        sht = book.sheets[sheet]
        df: pd.DataFrame = sht.range("A1").options(pd.DataFrame, expand="table").value
        book.save()  # keep any Excel auto‑conversions
        book.close()
    df.columns = df.columns.str.lower()
    return df.dropna(how="all")


def write_calc(book_path: str, sheet: str, df: pd.DataFrame) -> None:
    with xw.App(visible=False) as app:
        book = app.books.open(book_path)
        sht = book.sheets[sheet]
        sht.clear_contents()
        sht.range("A1").options(index=False).value = df
        book.save()
        book.close()

# ib_trade_engine/calc.py
from __future__ import annotations
from decimal import Decimal, ROUND_FLOOR
import pandas as pd


def calc_shares(df: pd.DataFrame) -> pd.DataFrame:
    def _shares(row):
        px_base = Decimal(str(row["last_base"]))
        if px_base <= 0:
            return 0
        qty = (Decimal(str(row["notional"])) / px_base).to_integral_value(rounding=ROUND_FLOOR)
        return int(qty)

    df["shares"] = df.apply(_shares, axis=1)
    return df

# ib_trade_engine/generate_qty.py
"""CLI or xlwings entry‑point to calculate share quantities."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd

from .ib_client import IBClient
from .excel_io import read_orders, write_calc
from .price_service import resolve_contract, snapshot, fx_rate
from .calc import calc_shares
from .database import init_db, dump

CONFIG_PATH = Path(__file__).with_suffix("").parent.parent / "config" / "settings.yaml"


def load_config(path=CONFIG_PATH):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()

    book_path = cfg["excel"]["workbook_path"]
    orders_df = read_orders(book_path, cfg["excel"]["input_sheet"])
    if orders_df.empty:
        print("No orders found in Excel; aborting.")
        return

    ibc = IBClient(cfg["ib"]["host"], cfg["ib"]["port"], cfg["ib"]["client_id"])
    ibc.connect()

    enriched_rows = []
    for _, row in orders_df.iterrows():
        symbol = str(row["symbol"]).strip().upper()
        notional = float(row["notional"])
        side = str(row["side"]).upper()
        base_ccy = (row.get("base_currency") or cfg["engine"].get("base_currency") or "USD").upper()

        contract = resolve_contract(ibc.ib, symbol)
        bid, ask, last = snapshot(ibc.ib, contract)
        fx = float(fx_rate(ibc.ib, contract.currency, base_ccy))
        last_base = last * fx

        enriched_rows.append({
            "symbol": symbol,
            "notional": notional,
            "side": side,
            "base_ccy": base_ccy,
            "bid": bid,
            "ask": ask,
            "last": last,
            "fx": fx,
            "last_base": last_base,
        })

    df = pd.DataFrame(enriched_rows)
    df = calc_shares(df)
    df.insert(0, "run_ts", datetime.utcnow().isoformat(timespec="seconds") + "Z")

    # Write back to Excel + DB
    write_calc(book_path, cfg["excel"]["output_sheet"], df)

    conn = init_db(cfg["engine"]["database"])
    dump(df, conn)
    conn.close()

    ibc.disconnect()
    print("✓ Quantity generation complete.")

if __name__ == "__main__":
    main()

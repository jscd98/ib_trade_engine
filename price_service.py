# ib_trade_engine/price_service.py
from __future__ import annotations
from decimal import Decimal
from typing import Tuple
from ib_insync import IB, Stock, Forex, util


def resolve_contract(ib: IB, symbol: str) -> Stock:
    details = ib.reqContractDetails(Stock(symbol, "SMART", "USD"))  # currency refined later
    if not details:
        raise ValueError(f"Symbol {symbol} not found on IB")
    return details[0].contract


def snapshot(ib: IB, contract):  # returns (bid, ask, last)
    ticker = ib.reqTickers(contract)[0]
    return ticker.bid, ticker.ask, ticker.last


def fx_rate(ib: IB, from_ccy: str, to_ccy: str) -> Decimal:
    if from_ccy == to_ccy:
        return Decimal("1")
    pair = f"{from_ccy}{to_ccy}"
    c = Forex(pair, "IDEALPRO")
    ticker = ib.reqTickers(c)[0]
    mid = (ticker.bid + ticker.ask) / 2
    if mid == 0:
        # try the inverse
        inv_pair = f"{to_ccy}{from_ccy}"
        c_inv = Forex(inv_pair, "IDEALPRO")
        t_inv = ib.reqTickers(c_inv)[0]
        mid = (t_inv.bid + t_inv.ask) / 2
        mid = 1 / mid if mid else 0
    if mid == 0:
        raise RuntimeError(f"No FX quote for {from_ccy}/{to_ccy}")
    return Decimal(str(mid))

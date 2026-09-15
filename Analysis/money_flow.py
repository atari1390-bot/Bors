from typing import Any, Optional


def _num(value) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _rows(data: Any) -> list:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("clientType", "clientTypes", "items", "Items", "data", "Data", "result", "Result"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    return []


def _value(row: dict, keys) -> Optional[float]:
    for key in keys:
        if key in row:
            value = _num(row.get(key))
            if value is not None:
                return value
    return None


def money_flow_analysis(client_type: Any) -> dict:
    rows = _rows(client_type)
    if not rows:
        return {
            "status": "NO_DATA", "real_buy": None, "real_sell": None,
            "legal_buy": None, "legal_sell": None, "real_money_flow": None, "buy_power": None,
        }

    real_buy_keys = ("buy_I_Volume", "buyI", "realBuy", "real_buy", "qTitMeDemReal", "volumeBuyReal")
    real_sell_keys = ("sell_I_Volume", "sellI", "realSell", "real_sell", "qTitMeOfReal", "volumeSellReal")
    legal_buy_keys = ("buy_N_Volume", "buyN", "legalBuy", "legal_buy", "volumeBuyLegal")
    legal_sell_keys = ("sell_N_Volume", "sellN", "legalSell", "legal_sell", "volumeSellLegal")

    real_buy = real_sell = legal_buy = legal_sell = None
    for row in rows:
        if not isinstance(row, dict):
            continue
        rb = _value(row, real_buy_keys)
        rs = _value(row, real_sell_keys)
        lb = _value(row, legal_buy_keys)
        ls = _value(row, legal_sell_keys)
        if rb is not None:
            real_buy = (real_buy or 0.0) + rb
        if rs is not None:
            real_sell = (real_sell or 0.0) + rs
        if lb is not None:
            legal_buy = (legal_buy or 0.0) + lb
        if ls is not None:
            legal_sell = (legal_sell or 0.0) + ls

    if real_buy is None or real_sell is None:
        return {
            "status": "UNPARSED", "real_buy": real_buy, "real_sell": real_sell,
            "legal_buy": legal_buy, "legal_sell": legal_sell,
            "real_money_flow": None, "buy_power": None,
        }

    return {
        "status": "OK",
        "real_buy": real_buy,
        "real_sell": real_sell,
        "legal_buy": legal_buy,
        "legal_sell": legal_sell,
        "real_money_flow": real_buy - real_sell,
        "buy_power": real_buy / real_sell if real_sell > 0 else None,
    }


analyze_money_flow = money_flow_analysis

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
        for key in (
            "bestLimits", "BestLimits", "items", "Items", "data", "Data", "result", "Result",
        ):
            value = data.get(key)
            if isinstance(value, list):
                return value
        if any(k in data for k in ("pMeDem", "pMeOf", "qTitMeDem", "qTitMeOf")):
            return [data]
    return []


def _value(row: dict, keys) -> Optional[float]:
    for key in keys:
        if key in row:
            value = _num(row.get(key))
            if value is not None:
                return value
    return None


def orderbook_analysis(orderbook: Any) -> dict:
    rows = _rows(orderbook)
    if not rows:
        return {
            "status": "NO_DATA", "best_buy": None, "best_sell": None,
            "buy_volume": 0.0, "sell_volume": 0.0, "buy_sell_ratio": None, "queue": "UNKNOWN",
        }

    buys, sells = [], []
    for row in rows:
        if not isinstance(row, dict):
            continue
        bp = _value(row, ("pMeDem", "priceBuy", "buyPrice", "PriceBuy", "buy_price"))
        sp = _value(row, ("pMeOf", "priceSell", "sellPrice", "PriceSell", "sell_price"))
        bq = _value(row, ("qTitMeDem", "buyVolume", "volumeBuy", "BuyVolume", "buy_volume"))
        sq = _value(row, ("qTitMeOf", "sellVolume", "volumeSell", "SellVolume", "sell_volume"))
        if bp is not None:
            buys.append({"price": bp, "volume": bq or 0.0})
        if sp is not None:
            sells.append({"price": sp, "volume": sq or 0.0})

    buy_volume = sum(x["volume"] for x in buys)
    sell_volume = sum(x["volume"] for x in sells)
    ratio = buy_volume / sell_volume if sell_volume > 0 else None

    if buy_volume > 0 and sell_volume == 0:
        queue = "BUY_QUEUE"
    elif sell_volume > 0 and buy_volume == 0:
        queue = "SELL_QUEUE"
    elif ratio is None:
        queue = "UNKNOWN"
    elif ratio >= 2:
        queue = "BUY_PRESSURE"
    elif ratio <= 0.5:
        queue = "SELL_PRESSURE"
    else:
        queue = "BALANCED"

    return {
        "status": "OK",
        "best_buy": max((x["price"] for x in buys), default=None),
        "best_sell": min((x["price"] for x in sells), default=None),
        "buy_volume": buy_volume,
        "sell_volume": sell_volume,
        "buy_sell_ratio": ratio,
        "queue": queue,
        "buy_levels": buys,
        "sell_levels": sells,
    }


analyze_orderbook = orderbook_analysis

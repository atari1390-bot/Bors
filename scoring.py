def _num(value, default=None):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def score_stock(technical, orderbook, money_flow, validation):
    technical = technical or {}
    orderbook = orderbook or {}
    money_flow = money_flow or {}
    validation = validation or {}

    data_score = 10 if validation.get("ok") is True else (3 if validation.get("status") == "NEEDS_REVIEW" else 0)

    technical_score = 0.0
    rsi = _num(technical.get("rsi_14"))
    if rsi is not None:
        if 45 <= rsi <= 65:
            technical_score += 10
        elif 35 <= rsi < 45:
            technical_score += 7
        elif 65 < rsi <= 75:
            technical_score += 6
        elif rsi < 30:
            technical_score += 3
        elif rsi > 75:
            technical_score += 2

    technical_score += 5 if technical.get("above_sma20") else 0
    technical_score += 5 if technical.get("above_sma50") else 0
    technical_score += 4 if technical.get("above_sma100") else 0
    technical_score += 4 if technical.get("above_sma200") else 0

    macd = _num(technical.get("macd"))
    macd_signal = _num(technical.get("macd_signal"))
    if macd is not None and macd_signal is not None and macd > macd_signal:
        technical_score += 4

    volume_ratio = _num(technical.get("volume_ratio"))
    if volume_ratio is not None:
        if volume_ratio >= 1.5:
            technical_score += 4
        elif volume_ratio >= 1.0:
            technical_score += 2

    technical_score = min(technical_score, 40.0)

    ratio = _num(orderbook.get("buy_sell_ratio"), _num(orderbook.get("buy_pressure")))
    orderbook_score = 0.0
    if ratio is not None:
        if ratio >= 2:
            orderbook_score += 15
        elif ratio >= 1.5:
            orderbook_score += 12
        elif ratio >= 1:
            orderbook_score += 8
        else:
            orderbook_score += 2

    queue = orderbook.get("queue")
    if queue == "BUY_QUEUE":
        orderbook_score += 5
    elif queue == "BUY_PRESSURE":
        orderbook_score += 3
    elif queue in ("SELL_QUEUE", "SELL_PRESSURE"):
        orderbook_score -= 5
    orderbook_score = max(0.0, min(orderbook_score, 25.0))

    flow_score = 0.0
    real_flow = _num(money_flow.get("real_money_flow"))
    buy_power = _num(money_flow.get("buy_power"))
    if real_flow is not None and real_flow > 0:
        flow_score += 15
    if buy_power is not None:
        if buy_power >= 2:
            flow_score += 10
        elif buy_power >= 1.5:
            flow_score += 7
        elif buy_power >= 1:
            flow_score += 4
    flow_score = min(flow_score, 25.0)

    total = round(max(0.0, min(100.0, data_score + technical_score + orderbook_score + flow_score)), 2)
    return {
        "score": total,
        "data_score": data_score,
        "technical_score": round(technical_score, 2),
        "orderbook_score": round(orderbook_score, 2),
        "money_flow_score": round(flow_score, 2),
    }


calculate_score = score_stock

from typing import Optional


def _num(value, default=None) -> Optional[float]:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _round_price(value):
    if value is None:
        return None
    value = float(value)
    if value >= 10000:
        return round(value / 100) * 100
    if value >= 1000:
        return round(value / 10) * 10
    return round(value)


def _current_price(snapshot, technical):
    closing = (snapshot or {}).get("closing")
    if isinstance(closing, dict):
        for key in ("pClosing", "price", "lastPrice", "last", "closingPrice", "PClosing"):
            value = _num(closing.get(key))
            if value is not None:
                return value
    if isinstance(closing, (int, float)):
        return float(closing)
    return _num((technical or {}).get("last_close"))


def build_signal(snapshot, technical, orderbook, money_flow, score):
    snapshot = snapshot or {}
    technical = technical or {}
    orderbook = orderbook or {}
    money_flow = money_flow or {}
    score = score or {}

    current = _current_price(snapshot, technical)
    total_score = _num(score.get("score"), 0.0)
    support = _num(technical.get("support_20"))
    resistance = _num(technical.get("resistance_20"))
    warnings = []

    if current is None:
        return {
            "status": "NEEDS_REVIEW", "score": total_score, "decision": "بررسی داده",
            "entry_1": None, "entry_2": None, "stop": None,
            "support": support, "resistance": resistance,
            "target_1": None, "target_2": None, "risk_reward": None,
            "warnings": ["قیمت جاری قابل استخراج نیست؛ سیگنال قابل اعتماد نیست."],
        }

    if support is None:
        support = current * 0.95
        warnings.append("حمایت از تقریب ۵٪ زیر قیمت محاسبه شد.")
    if resistance is None:
        resistance = current * 1.05
        warnings.append("مقاومت از تقریب ۵٪ بالای قیمت محاسبه شد.")

    if orderbook.get("queue") in ("SELL_QUEUE", "SELL_PRESSURE"):
        warnings.append("فشار عرضه در دفتر سفارش.")
    if money_flow.get("status") != "OK":
        warnings.append("جریان پول حقیقی از داده TSETMC به‌طور کامل خوانده نشده است.")

    sma20 = _num(technical.get("sma_20"))
    rsi = _num(technical.get("rsi_14"))
    ratio = _num(orderbook.get("buy_sell_ratio"))

    entry_1 = _round_price(max(support, current * 0.985))
    entry_2 = _round_price(current)
    stop = _round_price(support * 0.97)
    target_1 = _round_price(max(resistance, current * 1.05))
    target_2 = _round_price(current * 1.12)

    risk = current - (support * 0.97)
    reward = target_1 - current
    rr = round(reward / risk, 2) if risk > 0 else None

    if total_score >= 75 and (rsi is None or rsi < 75):
        decision = "خرید پله‌ای"
    elif total_score >= 60:
        decision = "مراقبت / تأیید"
    else:
        decision = "عدم ورود" if total_score < 40 else "مراقبت / تأیید"

    if sma20 is not None and current < sma20 and decision == "خرید پله‌ای":
        decision = "مراقبت / تأیید"
        warnings.append("قیمت زیر SMA20 است؛ ورود تهاجمی تأیید نشده.")
    if ratio is not None and ratio < 0.75 and decision == "خرید پله‌ای":
        decision = "مراقبت / تأیید"
        warnings.append("نسبت تقاضا به عرضه ضعیف است.")
    if rr is not None and rr < 1.5 and decision == "خرید پله‌ای":
        decision = "مراقبت / تأیید"
        warnings.append("نسبت ریسک به بازده کمتر از ۱.۵ است.")

    return {
        "status": "OK", "score": total_score, "decision": decision,
        "entry_1": entry_1, "entry_2": entry_2, "stop": stop,
        "support": _round_price(support), "resistance": _round_price(resistance),
        "target_1": target_1, "target_2": target_2, "risk_reward": rr,
        "warnings": warnings,
    }


generate_signal = build_signal

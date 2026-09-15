from typing import Any, Optional

import numpy as np
import pandas as pd


def _find_column(df: pd.DataFrame, candidates) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _rows_from_history(history: Any) -> list:
    if isinstance(history, list):
        return history
    if isinstance(history, dict):
        for key in (
            "closingPriceDaily", "closingPriceDailyList", "items", "Items",
            "data", "Data", "values",
        ):
            value = history.get(key)
            if isinstance(value, list):
                return value
    return []


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    return rsi


def calculate_macd(series: pd.Series):
    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal, macd - signal


def technical_analysis(history: Any) -> dict:
    rows = _rows_from_history(history)
    if not rows:
        return {"status": "NO_DATA"}

    df = pd.DataFrame(rows)
    if df.empty:
        return {"status": "NO_DATA"}

    close_col = _find_column(df, ("pClosing", "price", "close", "Close", "PClosing"))
    volume_col = _find_column(df, ("qTotTran5J", "volume", "Volume", "volumeValue"))
    if close_col is None:
        return {"status": "NO_DATA", "error": "ستون قیمت پایانی در تاریخچه پیدا نشد."}

    df[close_col] = pd.to_numeric(df[close_col], errors="coerce")
    df = df.dropna(subset=[close_col]).reset_index(drop=True)
    if df.empty:
        return {"status": "NO_DATA"}

    close = df[close_col].astype(float)
    current = float(close.iloc[-1])
    result = {"status": "OK", "last_close": current, "history_count": int(len(close))}

    for period in (20, 50, 100, 200):
        result[f"sma_{period}"] = (
            float(close.rolling(period).mean().iloc[-1]) if len(close) >= period else None
        )

    rsi = calculate_rsi(close)
    result["rsi_14"] = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None

    macd, signal, histogram = calculate_macd(close)
    result["macd"] = float(macd.iloc[-1])
    result["macd_signal"] = float(signal.iloc[-1])
    result["macd_histogram"] = float(histogram.iloc[-1])

    lookback = min(20, len(close))
    result["support_20"] = float(close.tail(lookback).min())
    result["resistance_20"] = float(close.tail(lookback).max())

    if volume_col is not None:
        df[volume_col] = pd.to_numeric(df[volume_col], errors="coerce")
        volume = df[volume_col].dropna()
        if len(volume):
            result["volume_last"] = float(volume.iloc[-1])
            result["volume_avg_20"] = float(volume.tail(min(20, len(volume))).mean())
            result["volume_ratio"] = (
                result["volume_last"] / result["volume_avg_20"]
                if result["volume_avg_20"] > 0 else None
            )
        else:
            result.update({"volume_last": None, "volume_avg_20": None, "volume_ratio": None})
    else:
        result.update({"volume_last": None, "volume_avg_20": None, "volume_ratio": None})

    for period in (20, 50, 100, 200):
        sma = result[f"sma_{period}"]
        result[f"above_sma{period}"] = sma is not None and current > sma

    return result


analyze_technical = technical_analysis

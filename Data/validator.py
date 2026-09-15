from typing import Any


def validate_snapshot(snapshot: Any) -> dict:
    if not isinstance(snapshot, dict):
        return {"status": "NEEDS_REVIEW", "ok": False, "missing": ["snapshot"]}

    required = ("closing", "orderbook", "client_type", "history")
    missing = [key for key in required if snapshot.get(key) is None]
    if missing:
        return {"status": "NEEDS_REVIEW", "ok": False, "missing": missing}
    return {"status": "OK", "ok": True, "missing": []}


def validate_tsetmc_data(data: Any) -> dict:
    return validate_snapshot(data)


def validate_instrument_search(data: Any) -> dict:
    if data is None or data == {} or data == []:
        return {"status": "NEEDS_REVIEW", "ok": False}
    return {"status": "OK", "ok": True}

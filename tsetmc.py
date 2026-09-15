import os
from typing import Any, Optional

import requests


class TSETMCError(RuntimeError):
    pass


class TSETMC:
    BASE_URL = "https://cdn.tsetmc.com/api"

    def __init__(self, timeout: Optional[int] = None):
        self.timeout = timeout or int(os.getenv("TSETMC_TIMEOUT", "15"))
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10) "
                "AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.tsetmc.com/",
        })

    def _get(self, path: str) -> Any:
        url = f"{self.BASE_URL}{path}"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            raise TSETMCError(f"پاسخ JSON معتبر نبود: {url}") from exc

    def search_instrument(self, symbol: str) -> Any:
        return self._get(f"/Instrument/GetInstrumentSearch/{symbol}")

    def closing_price(self, instrument_id: str) -> Any:
        return self._get(f"/ClosingPrice/GetClosingPriceInfo/{instrument_id}")

    def order_book(self, instrument_id: str) -> Any:
        return self._get(f"/BestLimits/{instrument_id}")

    def client_type(self, instrument_id: str) -> Any:
        return self._get(f"/ClientType/GetClientType/{instrument_id}/1/0")

    def daily_history(self, instrument_id: str) -> Any:
        return self._get(f"/ClosingPrice/GetClosingPriceDailyList/{instrument_id}/0")

    def snapshot(self, symbol: str) -> dict:
        search = self.search_instrument(symbol)
        instrument_id = self._extract_instrument_id(search)
        if not instrument_id:
            raise TSETMCError(f"نماد در TSETMC پیدا نشد: {symbol}")
        return {
            "symbol": symbol,
            "instrument_id": instrument_id,
            "closing": self.closing_price(instrument_id),
            "orderbook": self.order_book(instrument_id),
            "client_type": self.client_type(instrument_id),
            "history": self.daily_history(instrument_id),
        }

    @classmethod
    def _extract_instrument_id(cls, data: Any) -> Optional[str]:
        if data is None:
            return None
        if isinstance(data, list):
            for item in data:
                found = cls._extract_instrument_id(item)
                if found:
                    return str(found)
            return None
        if isinstance(data, dict):
            for key in (
                "insCode", "InsCode", "instrumentId", "InstrumentId",
                "instrumentID", "InstrumentID", "id", "ID",
            ):
                value = data.get(key)
                if value not in (None, ""):
                    return str(value)
            for key in (
                "instrument", "Instrument", "data", "Data", "items", "Items",
                "result", "Result", "trades", "Trades",
            ):
                if key in data:
                    found = cls._extract_instrument_id(data[key])
                    if found:
                        return str(found)
        return None

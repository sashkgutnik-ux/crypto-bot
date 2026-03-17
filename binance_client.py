import time
import hmac
import hashlib
import requests


class BinanceClient:
    def __init__(self):
        self.API_KEY = "r56MESicmmVM5XlD6k12c5FKz8aqtHsDNMD9tHVwnHHbBU5wBXss6QmHBQs7lU6a"
        self.API_SECRET = "gOHq0bj1a5U2cS5xa1FpLrglEXS0ytm6pSxLsIAwYz3T3YemWYBy5SRvipr8Alvw"
        self.BASE_URL = "https://fapi.binance.com"

    def _timestamp(self):
        return int(time.time() * 1000)

    def _sign(self, query):
        return hmac.new(
            self.API_SECRET.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()

    def _request(self, method, endpoint, params=None):
        if params is None:
            params = {}

        params["timestamp"] = self._timestamp()

        query = "&".join([f"{k}={params[k]}" for k in params])
        signature = self._sign(query)

        url = f"{self.BASE_URL}{endpoint}?{query}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.API_KEY}

        if method == "GET":
            r = requests.get(url, headers=headers)
        else:
            r = requests.post(url, headers=headers)

        data = r.json()

        if "code" in data and data["code"] < 0:
            print("❌ Binance Futures error:", data)

        return data

    # ===== BALANCE =====
    def get_balance(self):
        data = self._request("GET", "/fapi/v2/account")

        for asset in data["assets"]:
            if asset["asset"] == "USDT":
                return float(asset["availableBalance"])

        return 0

    # ===== SET LEVERAGE =====
    def set_leverage(self, symbol, leverage):
        return self._request("POST", "/fapi/v1/leverage", {
            "symbol": symbol,
            "leverage": leverage
        })

    # ===== MARKET ORDER =====
    def order(self, symbol, side, qty):
        return self._request("POST", "/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": qty
        })

    # ===== CLOSE POSITION =====
    def close_position(self, symbol, side, qty):
        opposite = "SELL" if side == "BUY" else "BUY"
        return self.order(symbol, opposite, qty)

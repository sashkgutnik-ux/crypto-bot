import time
import hmac
import hashlib
import requests


class BinanceClient:
    def __init__(self):
        self.API_KEY = "r56MESicmmVM5XlD6k12c5FKz8aqtHsDNMD9tHVwnHHbBU5wBXss6QmHBQs7lU6a"
        self.API_SECRET = "gOHq0bj1a5U2cS5xa1FpLrglEXS0ytm6pSxLsIAwYz3T3YemWYBy5SRvipr8Alvw"
        self.BASE_URL = "https://api.binance.com"

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
        params["recvWindow"] = 5000

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
            print("❌ Binance error:", data)

        return data

    # ===== BALANCE =====
    def get_balance(self, asset):
        data = self._request("GET", "/api/v3/account")

        if "balances" not in data:
            return 0

        for b in data["balances"]:
            if b["asset"] == asset:
                return float(b["free"])

        return 0

    # ===== SPOT BUY =====
    def buy(self, symbol, qty):
        return self._request("POST", "/api/v3/order", {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": qty
        })

    # ===== SPOT SELL =====
    def sell(self, symbol, qty):
        return self._request("POST", "/api/v3/order", {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": qty
        })

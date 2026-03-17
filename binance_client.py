import time
import hmac
import hashlib
import requests


class BinanceClient:
    def __init__(self):
        self.API_KEY = "r56MESicmmVM5XlD6k12c5FKz8aqtHsDNMD9tHVwnHHbBU5wBXss6QmHBQs7lU6a"
        self.API_SECRET = "gOHq0bj1a5U2cS5xa1FpLrglEXS0ytm6pSxLsIAwYz3T3YemWYBy5SRvipr8Alvw"

        self.BASE_URL = "https://api.binance.com"
        self.FUTURES_URL = "https://fapi.binance.com"

    def _timestamp(self):
        return int(time.time() * 1000)

    def _sign(self, query):
        return hmac.new(
            self.API_SECRET.encode(),
            query.encode(),
            hashlib.sha256
        ).hexdigest()

    def _request(self, method, endpoint, params=None, futures=False):
        if params is None:
            params = {}

        base = self.FUTURES_URL if futures else self.BASE_URL

        params["timestamp"] = self._timestamp()
        params["recvWindow"] = 5000

        query = "&".join([f"{k}={params[k]}" for k in params])
        signature = self._sign(query)

        url = f"{base}{endpoint}?{query}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.API_KEY}

        if method == "GET":
            r = requests.get(url, headers=headers)
        else:
            r = requests.post(url, headers=headers)

        data = r.json()

        if "code" in data and data["code"] < 0:
            print("❌ Binance error:", data)

        return data

    # ===== SPOT =====
    def get_balance(self, asset):
        data = self._request("GET", "/api/v3/account")

        if "balances" not in data:
            return 0

        for b in data["balances"]:
            if b["asset"] == asset:
                return float(b["free"])

        return 0

    def spot_buy(self, symbol, qty):
        return self._request("POST", "/api/v3/order", {
            "symbol": symbol,
            "side": "BUY",
            "type": "MARKET",
            "quantity": qty
        })

    def spot_sell(self, symbol, qty):
        return self._request("POST", "/api/v3/order", {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": qty
        })

    # ===== FUTURES =====
    def get_position(self, symbol):
        data = self._request("GET", "/fapi/v2/positionRisk", {}, futures=True)

        for p in data:
            if p["symbol"] == symbol:
                return float(p["positionAmt"])

        return 0

    def futures_order(self, symbol, side, qty):
        return self._request("POST", "/fapi/v1/order", {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": qty
        }, futures=True)

    def set_stop_loss(self, symbol, side, stop_price):
        return self._request("POST", "/fapi/v1/order", {
            "symbol": symbol,
            "side": "SELL" if side == "BUY" else "BUY",
            "type": "STOP_MARKET",
            "stopPrice": round(stop_price, 2),
            "closePosition": "true"
        }, futures=True)

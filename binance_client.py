import requests
import time
import hmac
import hashlib


class BinanceClient:
    def __init__(self):
        self.API_KEY = "YOUR_API_KEY"
        self.API_SECRET = "YOUR_SECRET_KEY"
        self.BASE_URL = "https://api.binance.com"

    def _get_signature(self, query_string):
        return hmac.new(
            self.API_SECRET.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()

    def _headers(self):
        return {
            "X-MBX-APIKEY": self.API_KEY
        }

    def get_balance(self, asset):
        url = "/api/v3/account"

        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}"
        signature = self._get_signature(query_string)

        full_url = self.BASE_URL + url + "?" + query_string + "&signature=" + signature

        response = requests.get(full_url, headers=self._headers())
        data = response.json()

        for bal in data["balances"]:
            if bal["asset"] == asset:
                return float(bal["free"])

        return 0.0

    def market_buy(self, symbol, quantity):
        print(f"🚀 MARKET BUY {quantity} {symbol}")

    def market_sell(self, symbol, quantity):
        print(f"🚀 MARKET SELL {quantity} {symbol}")

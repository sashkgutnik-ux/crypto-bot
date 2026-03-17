import requests
import time
import hmac
import hashlib


class BinanceClient:
    def __init__(self):
        self.API_KEY = "r56MESicmmVM5XlD6k12c5FKz8aqtHsDNMD9tHVwnHHbBU5wBXss6QmHBQs7lU6a"
        self.API_SECRET = "gOHq0bj1a5U2cS5xa1FpLrglEXS0ytm6pSxLsIAwYz3T3YemWYBy5SRvipr8Alvw"
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
        try:
            url = "/api/v3/account"

            timestamp = int(time.time() * 1000)
            query_string = f"timestamp={timestamp}"
            signature = self._get_signature(query_string)

            full_url = f"{self.BASE_URL}{url}?{query_string}&signature={signature}"

            response = requests.get(full_url, headers=self._headers())
            data = response.json()

            # 🔥 ОБРАБОТКА ОШИБОК
            if "balances" not in data:
                print("❌ Binance API ERROR:", data)
                return 0.0

            for bal in data["balances"]:
                if bal["asset"] == asset:
                    return float(bal["free"])

            return 0.0

        except Exception as e:
            print("❌ Balance error:", e)
            return 0.0

    def market_buy(self, symbol, quantity):
        try:
            url = "/api/v3/order"

            timestamp = int(time.time() * 1000)

            params = {
                "symbol": symbol,
                "side": "BUY",
                "type": "MARKET",
                "quantity": quantity,
                "timestamp": timestamp
            }

            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            signature = self._get_signature(query_string)

            full_url = f"{self.BASE_URL}{url}?{query_string}&signature={signature}"

            response = requests.post(full_url, headers=self._headers())
            data = response.json()

            print("🟢 BUY ORDER:", data)

        except Exception as e:
            print("❌ BUY ERROR:", e)

    def market_sell(self, symbol, quantity):
        try:
            url = "/api/v3/order"

            timestamp = int(time.time() * 1000)

            params = {
                "symbol": symbol,
                "side": "SELL",
                "type": "MARKET",
                "quantity": quantity,
                "timestamp": timestamp
            }

            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            signature = self._get_signature(query_string)

            full_url = f"{self.BASE_URL}{url}?{query_string}&signature={signature}"

            response = requests.post(full_url, headers=self._headers())
            data = response.json()

            print("🔴 SELL ORDER:", data)

        except Exception as e:
            print("❌ SELL ERROR:", e)

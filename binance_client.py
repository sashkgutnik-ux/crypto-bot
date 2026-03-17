import requests
import time
import hmac
import hashlib


class BinanceClient:
    def __init__(self):
        self.API_KEY = "eCWy1i5O1Lh1pcUQwHNVeXSTPF6iAvJAEzD0MCun050Sq6jZyWDlFbbQjPX2e73w
"
        self.API_SECRET = "kkiygYBvpMADFOTNwbDFV3kv65HsvonOXqwRuSDZLf4GlHYwyaSQjh7zDBHRY4tZ"
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

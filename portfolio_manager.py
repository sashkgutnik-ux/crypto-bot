import requests


class BybitConnector:

    def __init__(self):
        self.base_url = "https://api.bybit.com"

    def get_price(self, symbol="BTCUSDT"):

        url = f"{self.base_url}/v5/market/tickers?category=linear&symbol={symbol}"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        try:

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print("HTTP ERROR:", response.status_code)
                return None

            data = response.json()

            price = float(data["result"]["list"][0]["lastPrice"])

            return price

        except Exception as e:

            print("API ERROR:", e)
            return None
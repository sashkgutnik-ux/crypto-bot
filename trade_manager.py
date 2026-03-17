import requests


class BinanceHistory:

    def __init__(self, symbol="BTCUSDT", interval="1m", limit=500):
        self.symbol = symbol
        self.interval = interval
        self.limit = limit

    def get_klines(self):

        url = "https://api.binance.com/api/v3/klines"

        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "limit": self.limit
        }

        response = requests.get(url, params=params)
        data = response.json()

        prices = []

        # Проверяем что Binance вернул список свечей
        if not isinstance(data, list):
            print("Binance API Error:", data)
            return []

        for candle in data:

            # проверяем что свеча корректная
            if len(candle) < 5:
                continue

            close_price = float(candle[4])
            prices.append(close_price)

        return prices

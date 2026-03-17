import requests

def get_historical_prices(symbol="BTCUSDT", limit=200):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1m",
        "limit": limit
    }

    response = requests.get(url, params=params)
    data = response.json()

    prices = [float(candle[4]) for candle in data]

    return prices

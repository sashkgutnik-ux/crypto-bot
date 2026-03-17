import requests
import pandas as pd


def get_candles():

    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 100
    }

    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data)

    df = df[[0,1,2,3,4]]

    df.columns = ["time","open","high","low","close"]

    df["close"] = df["close"].astype(float)

    return df


# ===== EMA =====

def ema(series, period):

    return series.ewm(span=period, adjust=False).mean()


# ===== RSI =====

def rsi(series, period=14):

    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss

    return 100 - (100 / (1 + rs))


# ===== Bollinger =====

def bollinger(series, period=20):

    ma = series.rolling(window=period).mean()

    std = series.rolling(window=period).std()

    upper = ma + (std * 2)

    lower = ma - (std * 2)

    return upper, lower


def calculate_indicators():

    df = get_candles()

    df["ema9"] = ema(df["close"], 9)
    df["ema21"] = ema(df["close"], 21)

    df["rsi"] = rsi(df["close"])

    upper, lower = bollinger(df["close"])

    df["bb_upper"] = upper
    df["bb_lower"] = lower

    return df

import requests


def get_market_data():
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "1m", "limit": 100}
    data = requests.get(url, params=params).json()

    closes = [float(c[4]) for c in data]
    highs = [float(c[2]) for c in data]
    lows = [float(c[3]) for c in data]

    return closes, highs, lows


def ema(data, period):
    k = 2 / (period + 1)
    ema_val = data[0]

    for price in data:
        ema_val = price * k + ema_val * (1 - k)

    return ema_val


def rsi(data, period=14):
    gains = []
    losses = []

    for i in range(1, len(data)):
        diff = data[i] - data[i - 1]
        if diff > 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0.0001
    avg_loss = sum(losses[-period:]) / period if losses else 0.0001

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def choose_best_strategy(price):
    closes, highs, lows = get_market_data()

    ema50 = ema(closes, 50)
    ema200 = ema(closes, 200)
    rsi_val = rsi(closes)

    volatility = max(highs[-20:]) - min(lows[-20:])

    scores = {
        "EMA": 0,
        "RSI": 0,
        "Breakout": 0,
        "Bollinger": 0,
        "Grid": 0,
    }

    # ===== EMA =====
    if ema50 > ema200:
        scores["EMA"] += 30
    else:
        scores["EMA"] += 10

    # ===== RSI =====
    if rsi_val < 30 or rsi_val > 70:
        scores["RSI"] += 25
    else:
        scores["RSI"] += 10

    # ===== Breakout =====
    if volatility > price * 0.01:
        scores["Breakout"] += 30
    else:
        scores["Breakout"] += 10

    # ===== Bollinger =====
    if 30 < rsi_val < 70:
        scores["Bollinger"] += 20
    else:
        scores["Bollinger"] += 10

    # ===== Grid =====
    if volatility < price * 0.005:
        scores["Grid"] += 25
    else:
        scores["Grid"] += 5

    # ===== НОРМАЛИЗАЦИЯ ДО 100% =====
    total = sum(scores.values())

    for k in scores:
        scores[k] = round(scores[k] / total * 100, 2)

    return scores

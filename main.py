import time
import requests
from binance_client import BinanceClient

# ===== ВСТАВЬ СВОИ ДАННЫЕ =====
API_KEY = "r56MESicmmVM5XlD6k12c5FKz8aqtHsDNMD9tHVwnHHbBU5wBXss6QmHBQs7lU6a"
API_SECRET = "gOHq0bj1a5U2cS5xa1FpLrglEXS0ytm6pSxLsIAwYz3T3YemWYBy5SRvipr8Alvw"

TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

SYMBOL = "BTCUSDC"
SLEEP = 30

client = BinanceClient(API_KEY, API_SECRET)

# ===== TELEGRAM =====
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== RSI =====
def rsi(prices, period=14):
    gains, losses = [], []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ===== EMA =====
def ema(prices, period):
    k = 2 / (period + 1)
    e = prices[0]
    for p in prices:
        e = p * k + e * (1 - k)
    return e

# ===== ДАННЫЕ =====
def get_prices():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=1m&limit=100"
    data = requests.get(url).json()
    return [float(c[4]) for c in data]

# ===== БОТ =====
def run():
    print("🚀 BOT STARTED")
    send("🚀 Bot started")

    in_position = False

    while True:
        try:
            prices = get_prices()

            price = prices[-1]
            e50 = ema(prices, 50)
            e200 = ema(prices, 200)
            r = rsi(prices)

            usdc = client.get_balance("USDC")
            btc = client.get_balance("BTC")

            print(f"PRICE: {price}")
            print(f"EMA50: {e50} EMA200: {e200} RSI: {r}")
            print(f"USDC: {usdc} BTC: {btc}")

            # BUY
            if e50 > e200 and r < 35 and not in_position:
                if usdc > 5:
                    qty = (usdc * 0.95) / price
                    client.order(SYMBOL, "BUY", round(qty, 5))
                    send(f"🟢 BUY BTC {price}")
                    in_position = True

            # SELL
            elif e50 < e200 and r > 65 and in_position:
                if btc > 0.0001:
                    client.order(SYMBOL, "SELL", round(btc, 5))
                    send(f"🔴 SELL BTC {price}")
                    in_position = False

            else:
                print("HOLD")

        except Exception as e:
            print("ERROR:", e)

        time.sleep(SLEEP)

run()

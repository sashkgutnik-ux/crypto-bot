import time
import requests
from collections import deque
from binance.client import Client

# =========================
# PROXY (FIXED)
# =========================
PROXY_URL = "http://45.157.123.217:8000"
PROXY_AUTH = ("ORSn3J", "GWSWrc")

# =========================
# BINANCE TESTNET
# =========================
API_KEY = "eCWy1i5O1Lh1pcUQwHNVeXSTPF6iAvJAEzD0MCun050Sq6jZyWDlFbbQjPX2e73w"
API_SECRET = "kkiygYBvpMADFOTNwbDFV3kv65HsvonOXqwRuSDZLf4GlHYwyaSQjh7zDBHRY4tZ"

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

SYMBOL = "BTCUSDT"

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

def send(msg):
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg}
        )
    except:
        pass

# =========================
# P2P НАСТРОЙКИ
# =========================
SPREAD_MIN = -3.0
SPREAD_MAX = 3.0

# =========================
# HELPERS
# =========================
def get_price():
    return float(client.get_symbol_ticker(symbol=SYMBOL)["price"])

# =========================
# BINANCE P2P
# =========================
def get_binance_p2p():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

        data = {
            "asset": "USDT",
            "fiat": "EUR",
            "tradeType": "SELL",
            "page": 1,
            "rows": 5,
            "payTypes": ["SEPA"]
        }

        res = requests.post(url, json=data, timeout=10).json()
        offers = res.get("data", [])

        prices = []
        for o in offers:
            adv = o["adv"]
            advertiser = o["advertiser"]

            if advertiser["monthOrderCount"] >= 99:
                prices.append(float(adv["price"]))

        return min(prices) if prices else None

    except Exception as e:
        print("BINANCE ERROR:", e)
        return None

# =========================
# BYBIT P2P (через proxy FIX)
# =========================
def get_bybit_p2p():
    try:
        url = "https://api2.bybit.com/fiat/otc/item/online"

        data = {
            "tokenId": "USDT",
            "currencyId": "EUR",
            "side": "0",
            "page": 1,
            "size": 5
        }

        res = requests.post(
            url,
            json=data,
            proxies={
                "http": PROXY_URL,
                "https": PROXY_URL
            },
            auth=PROXY_AUTH,
            timeout=10
        ).json()

        offers = res.get("result", {}).get("items", [])

        prices = []
        for o in offers:
            if float(o["recentExecuteRate"]) >= 99:
                prices.append(float(o["price"]))

        return max(prices) if prices else None

    except Exception as e:
        print("BYBIT ERROR:", e)
        return None

# =========================
# P2P CHECK
# =========================
def check_p2p():
    binance_price = get_binance_p2p()
    bybit_price = get_bybit_p2p()

    print(f"DEBUG: {binance_price} | {bybit_price}")

    if not binance_price or not bybit_price:
        print("P2P NO DATA")
        return

    spread = (binance_price - bybit_price) / bybit_price * 100

    print(f"P2P SPREAD: {round(spread,2)}%")

    if SPREAD_MIN <= spread <= SPREAD_MAX:
        send(f"""
💰 P2P СВЯЗКА

Bybit BUY: {bybit_price}
Binance SELL: {binance_price}

Спред: {round(spread,2)}%
""")

# =========================
# STATE
# =========================
prices = deque(maxlen=50)

# =========================
# START
# =========================
print("🚀 BOT STARTED")
send("🚀 BOT STARTED")

while True:
    try:
        price = get_price()
        prices.append(price)

        print(f"PRICE: {price}")

        check_p2p()

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

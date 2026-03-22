import time
import requests
from binance.client import Client

# =========================
# PROXY (БЕЗ ЛОГИНА!)
# =========================
PROXY = {
    "http": "http://45.157.123.217:8000",
    "https": "http://45.157.123.217:8000"
}

# =========================
# BINANCE
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
            if o["advertiser"]["monthOrderCount"] >= 99:
                prices.append(float(o["adv"]["price"]))

        return min(prices) if prices else None

    except Exception as e:
        print("BINANCE ERROR:", e)
        return None

# =========================
# BYBIT P2P
# =========================
def get_bybit_p2p():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    data = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "0",
        "page": 1,
        "size": 5
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://www.bybit.com",
        "Referer": "https://www.bybit.com/"
    }

    proxies = {
        "http": "http://ORSn3J:GWSWrc@45.157.123.217:8000",
        "https": "http://ORSn3J:GWSWrc@45.157.123.217:8000"
    }

    for _ in range(3):  # retry 3 раза
        try:
            res = requests.post(
                url,
                json=data,
                headers=headers,
                proxies=proxies,
                timeout=20
            ).json()

            offers = res.get("result", {}).get("items", [])

            prices = []
            for o in offers:
                if float(o["recentExecuteRate"]) >= 99:
                    prices.append(float(o["price"]))

            if prices:
                return max(prices)

        except Exception as e:
            print("BYBIT RETRY ERROR:", e)

    return None

# =========================
# MAIN LOOP
# =========================
print("🚀 BOT STARTED")

while True:
    try:
        price = float(client.get_symbol_ticker(symbol=SYMBOL)["price"])
        print(f"PRICE: {price}")

        b = get_binance_p2p()
        y = get_bybit_p2p()

        print(f"DEBUG: {b} | {y}")

        if b and y:
            spread = (b - y) / y * 100
            print(f"SPREAD: {round(spread,2)}%")

            send(f"""
💰 P2P

Bybit: {y}
Binance: {b}
Spread: {round(spread,2)}%
""")
        else:
            print("P2P NO DATA")

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

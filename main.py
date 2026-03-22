import requests
import time

# =========================
# ВСТАВЬ СЮДА СВОИ ДАННЫЕ
# =========================
TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_bybit_price():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    headers = {
        "user-agent": "Mozilla/5.0",
        "origin": "https://www.bybit.com",
        "referer": "https://www.bybit.com/",
    }

    payload = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "1",
        "size": "10",
        "page": "1"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()
        prices = [float(x["price"]) for x in data["result"]["items"]]
        return min(prices)
    except:
        return None


def get_binance_price():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "BUY",
        "page": 1,
        "rows": 10
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        prices = [float(x["adv"]["price"]) for x in data["data"]]
        return min(prices)
    except:
        return None


print("BOT STARTED")

while True:
    bybit = get_bybit_price()
    binance = get_binance_price()

    if bybit and binance:
        spread = ((binance - bybit) / bybit) * 100

        msg = f"""BYBIT: {bybit}
BINANCE: {binance}
SPREAD: {round(spread, 2)}%"""

        print(msg)
        send_telegram(msg)

    else:
        print("ERROR")

    time.sleep(15)

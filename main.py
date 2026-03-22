import requests
import time

# 🔐 ВСТАВЬ СВОЁ
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"


# =========================
# 📊 BYBIT P2P
# =========================
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
        "side": "1",  # BUY
        "size": "10",
        "page": "1",

        # 💳 ТВОИ ФИЛЬТРЫ
        "payment": ["14", "62", "75"],  # Revolut, N26, Wise

        # 💰 СУММА КАК У ТЕБЯ
        "amount": "250"
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        data = r.json()

        items = data["result"]["items"]
        prices = [float(x["price"]) for x in items]

        return min(prices)

    except Exception as e:
        print("BYBIT ERROR:", e)
        return None


# =========================
# 📊 BINANCE P2P
# =========================
def get_binance_price():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "BUY",
        "transAmount": "250",  # 💰 сумма
        "page": 1,
        "rows": 10,

        # 💳 ТЕ ЖЕ МЕТОДЫ
        "payTypes": ["REVOLUT", "N26", "WISE"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()

        prices = [float(x["adv"]["price"]) for x in data["data"]]

        return min(prices)

    except Exception as e:
        print("BINANCE ERROR:", e)
        return None


# =========================
# 📩 TELEGRAM
# =========================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)


# =========================
# 🚀 MAIN LOOP
# =========================
print("🚀 BOT STARTED")

while True:
    bybit = get_bybit_price()
    binance = get_binance_price()

    print("BYBIT:", bybit)
    print("BINANCE:", binance)

    if bybit and binance:
        spread = ((binance - bybit) / bybit) * 100

        message = (
            f"BYBIT: {bybit}\n"
            f"BINANCE: {binance}\n"
            f"SPREAD: {round(spread, 2)}%"
        )

        print(message)
        send_telegram(message)

    time.sleep(15)

import requests
import time

# 🔐 ВСТАВЬ СВОЁ
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

AMOUNT = 250
DELTA_THRESHOLD = 0.02  # ≈2-3% норм сигнал

signal_active = False
last_ping = 0


# =========================
# 📩 TELEGRAM
# =========================
def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# =========================
# 📊 BYBIT (ТОП-3)
# =========================
def get_bybit_price():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    payload = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "1",
        "size": "10",
        "page": "1",
        "payment": ["14", "62", "75"],
    }

    for _ in range(3):  # 🔁 retry 3 раза
        try:
            r = requests.post(url, json=payload, timeout=20)  # увеличили timeout
            data = r.json()

            prices = []

            for item in data["result"]["items"]:
                price = float(item["price"])
                min_limit = float(item["minAmount"])
                max_limit = float(item["maxAmount"])
                orders = float(item["recentOrderNum"])

                if not (min_limit <= 250 <= max_limit):
                    continue

                if orders < 30:  # чуть мягче фильтр
                    continue

                prices.append(price)

            if len(prices) >= 3:
                prices.sort()
                return sum(prices[:3]) / 3

        except Exception as e:
            print("BYBIT RETRY:", e)
            time.sleep(3)

    return None


# =========================
# 📊 BINANCE (ТОП-3)
# =========================
def get_binance_price():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "BUY",
        "transAmount": str(AMOUNT),
        "page": 1,
        "rows": 10,
        "payTypes": ["REVOLUT", "N26", "WISE"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()

        prices = []

        for ad in data["data"]:
            price = float(ad["adv"]["price"])
            orders = float(ad["advertiser"]["monthOrderCount"])

            if orders < 50:
                continue

            prices.append(price)

        if len(prices) < 3:
            return None

        prices.sort()
        return sum(prices[:3]) / 3  # ТОП-3

    except Exception as e:
        print("BINANCE ERROR:", e)
        return None


# =========================
# 🚀 MAIN
# =========================
print("🚀 BOT STARTED")

while True:
    try:
        bybit = get_bybit_price()
        binance = get_binance_price()

        print("BYBIT:", bybit)
        print("BINANCE:", binance)

        if bybit and binance:
            delta = binance - bybit

            print(f"DELTA: {round(delta, 4)}")

            # 🔥 сигнал
            if delta >= DELTA_THRESHOLD:
                if not signal_active:
                    send_telegram(
                        f"🚀 СИГНАЛ\n\n"
                        f"BYBIT: {round(bybit, 4)}\n"
                        f"BINANCE: {round(binance, 4)}\n"
                        f"DELTA: {round(delta, 4)} €"
                    )
                    signal_active = True
            else:
                signal_active = False

        else:
            print("Нет данных")

        # ⏱ живой сигнал раз в 3 часа
        if time.time() - last_ping > 10800:
            send_telegram("✅ Бот работает")
            last_ping = time.time()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(20)

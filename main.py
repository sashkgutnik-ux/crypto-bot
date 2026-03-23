import requests
import time

# 🔐 ВСТАВЬ СВОЁ
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

AMOUNT = 250
SPREAD_TRIGGER = 0.005  # ~0.5%

last_signal = False
last_ping = 0


# =========================
# 📩 TELEGRAM
# =========================
def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


# =========================
# 📊 BYBIT (BUY)
# =========================
def get_bybit_price():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    payload = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "1",
        "size": "10",
        "page": "1",
        "payment": ["14", "62", "75"]
    }

    for _ in range(3):  # 🔁 retry
        try:
            r = requests.post(url, json=payload, timeout=15)
            data = r.json()

            prices = []

            for item in data["result"]["items"]:
                min_limit = float(item["minAmount"])
                max_limit = float(item["maxAmount"])

                if min_limit <= 250 <= max_limit:
                    prices.append(float(item["price"]))

            if prices:
                return round(min(prices), 3)

        except:
            time.sleep(2)

    return None


# =========================
# 📊 BINANCE (SELL)
# =========================
def get_binance_price():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "SELL",  # ❗ ВАЖНО
        "transAmount": str(AMOUNT),
        "page": 1,
        "rows": 10,
        "payTypes": ["REVOLUT", "N26", "WISE", "SEPA_INSTANT"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()

        valid_prices = []

        for item in data["data"]:
            adv = item["adv"]

            min_limit = float(adv["minSingleTransAmount"])
            max_limit = float(adv["maxSingleTransAmount"])

            if min_limit <= AMOUNT <= max_limit:
                price = float(adv["price"])
                valid_prices.append(price)

        return round(max(valid_prices), 3) if valid_prices else None  # продаем дороже

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
            spread = delta / bybit

            print(f"DELTA: {round(delta, 4)}")
            print(f"SPREAD: {round(spread*100, 2)}%")

            # 🔥 сигнал
            if spread >= SPREAD_TRIGGER:
                if not last_signal:
                    send_telegram(
                        f"🚀 СИГНАЛ\n\n"
                        f"Купить BYBIT: {bybit}\n"
                        f"Продать BINANCE: {binance}\n"
                        f"Δ: {round(delta,4)}\n"
                        f"{round(spread*100,2)}%"
                    )
                    last_signal = True
            else:
                last_signal = False

        else:
            print("Нет данных")

        # ⏱ жив
        if time.time() - last_ping > 10800:
            send_telegram("✅ Бот жив")
            last_ping = time.time()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(30)

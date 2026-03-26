import requests
import time

# 🔐 ВСТАВЬ СВОЁ
BOT_TOKEN = "ТВОЙ_ТОКЕН"
CHAT_ID = "ТВОЙ_CHAT_ID"

BASE_PRICE = 0.864  # 🔥 фикс байбит
AMOUNT = 250

TRIGGER_PERCENT = 0.6  # сигнал от 0.6%

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
# 📊 BINANCE SELL
# =========================
def get_binance_sell():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"

    payload = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "SELL",
        "transAmount": str(AMOUNT),
        "page": 1,
        "rows": 10,
        "payTypes": ["REVOLUT", "N26", "WISE", "SEPA_INSTANT"]
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()

        prices = []

        for item in data["data"]:
            adv = item["adv"]

            min_limit = float(adv["minSingleTransAmount"])
            max_limit = float(adv["maxSingleTransAmount"])

            if min_limit <= AMOUNT <= max_limit:
                prices.append(float(adv["price"]))

        return round(max(prices), 3) if prices else None

    except:
        return None


# =========================
# 📊 BYBIT SELL
# =========================
def get_bybit_sell():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    payload = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "0",  # 🔥 SELL
        "size": "10",
        "page": "1",
        "payment": ["14", "62", "75"]  # Revolut, N26, Wise
    }

    for _ in range(3):
        try:
            r = requests.post(url, json=payload, timeout=15)
            data = r.json()

            prices = []

            for item in data["result"]["items"]:
                min_limit = float(item["minAmount"])
                max_limit = float(item["maxAmount"])

                if min_limit <= AMOUNT <= max_limit:
                    prices.append(float(item["price"]))

            return round(max(prices), 3) if prices else None

        except:
            time.sleep(2)

    return None


# =========================
# 🚀 MAIN
# =========================
print("🚀 BOT STARTED")

while True:
    try:
        binance = get_binance_sell()
        bybit = get_bybit_sell()

        print("BASE:", BASE_PRICE)
        print("BINANCE SELL:", binance)
        print("BYBIT SELL:", bybit)

        signal_triggered = False

        # ===== BINANCE =====
        if binance:
            delta_binance = binance - BASE_PRICE
            percent_binance = (delta_binance / BASE_PRICE) * 100

            print(f"BINANCE Δ: {round(delta_binance,4)}")
            print(f"BINANCE %: {round(percent_binance,2)}%")

            if percent_binance >= TRIGGER_PERCENT:
                signal_triggered = True

        # ===== BYBIT =====
        if bybit:
            delta_bybit = bybit - BASE_PRICE
            percent_bybit = (delta_bybit / BASE_PRICE) * 100

            print(f"BYBIT Δ: {round(delta_bybit,4)}")
            print(f"BYBIT %: {round(percent_bybit,2)}%")

            if percent_bybit >= TRIGGER_PERCENT:
                signal_triggered = True

        # ===== СИГНАЛ =====
        if signal_triggered:
            if not last_signal:
                send_telegram(
                    f"🚀 ПЕРЕКОС\n\n"
                    f"BASE: {BASE_PRICE}\n\n"
                    f"BINANCE SELL: {binance}\n"
                    f"BYBIT SELL: {bybit}\n\n"
                    f"Проверь руками 🔥"
                )
                last_signal = True
        else:
            last_signal = False

        # ===== ПИНГ =====
        if time.time() - last_ping > 10800:
            send_telegram("✅ Бот жив")
            last_ping = time.time()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(30)

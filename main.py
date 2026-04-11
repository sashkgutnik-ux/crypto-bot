import requests
import time

# 🔐 ВСТАВЬ СВОЁ
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

BASE_PRICE = 0.855  # 🔥 фикс покупка
AMOUNT = 250

TRIGGER_PERCENT = 0.6

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
# 📊 BINANCE SELL (ТОЛЬКО НУЖНЫЕ ПЛАТЕЖКИ)
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
        "payTypes": [
            "WISE",
            "N26",
            "SEPA_INSTANT",
            "PAYSAFE",   # иногда это Paysera
            "SEPA",      # обычный банковский перевод ЕС
            "BUNQ"
        ]
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

    except Exception as e:
        print("BINANCE ERROR:", e)
        return None


# =========================
# 🚀 MAIN
# =========================
print("🚀 BOT STARTED")

while True:
    try:
        binance = get_binance_sell()

        print("BASE BUY:", BASE_PRICE)
        print("BINANCE SELL:", binance)

        if binance:
            delta = binance - BASE_PRICE
            percent = (delta / BASE_PRICE) * 100

            print(f"DELTA: {round(delta,4)}")
            print(f"PERCENT: {round(percent,2)}%")

            if percent >= TRIGGER_PERCENT:
                if not last_signal:
                    send_telegram(
                        f"🚀 СИГНАЛ\n\n"
                        f"Купить: {BASE_PRICE}\n"
                        f"Продать Binance: {binance}\n\n"
                        f"Δ: {round(delta,4)}\n"
                        f"{round(percent,2)}%"
                    )
                    last_signal = True
            else:
                last_signal = False

        else:
            print("Нет данных Binance")

        # ⏱ пинг
        if time.time() - last_ping > 10800:
            send_telegram("✅ Бот жив")
            last_ping = time.time()

    except Exception as e:
        print("ERROR:", e)

    time.sleep(30)

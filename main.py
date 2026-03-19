import time
import requests
from collections import deque

# =========================
# НАСТРОЙКИ
# =========================
SYMBOL = "BTCUSDT"

TRADE_AMOUNT = 100  # виртуальные USDT
TAKE_PROFIT = 0.025  # 2.5%
STOP_LOSS = 0.025  # 2.5%
DIP_THRESHOLD = -0.05  # -5%
SECOND_DIP = -0.03  # -3%

COOLDOWN = 900  # 15 мин

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
# ПОЛУЧЕНИЕ ЦЕНЫ
# =========================
def get_price():
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
    data = requests.get(url).json()
    return float(data["price"])

# =========================
# СОСТОЯНИЕ
# =========================
prices = deque(maxlen=50)

position = None
cooldown_until = 0

# =========================
# ВСПОМОГАТЕЛЬНОЕ
# =========================
def percent_change(old, new):
    return (new - old) / old

def is_stable():
    # последние 5 цен не делают новый минимум
    if len(prices) < 6:
        return False
    last = list(prices)[-6:]
    return min(last[:-1]) <= last[-1]

def bounce_detected():
    if len(prices) < 3:
        return False
    return prices[-1] > prices[-2] > prices[-3]

def btc_market_ok():
    # простой фильтр рынка (1 час ~ 12 точек)
    if len(prices) < 12:
        return True
    change = percent_change(prices[-12], prices[-1])
    return change > -0.05

# =========================
# ОСНОВНОЙ ЦИКЛ
# =========================
print("BOT STARTED")

while True:
    try:
        price = get_price()
        prices.append(price)

        print(f"Price: {price}")

        # =========================
        # НЕТ ПОЗИЦИИ → ИЩЕМ ВХОД
        # =========================
        if position is None and time.time() > cooldown_until:

            if len(prices) > 10:
                change = percent_change(prices[0], price)

                if change <= DIP_THRESHOLD and btc_market_ok():

                    if is_stable() or bounce_detected():

                        position = {
                            "entry": price,
                            "amount": TRADE_AMOUNT * 0.5,
                            "second_entry": None
                        }

                        send(f"🟢 BUY 1: {price}")
                        print("BUY 1")

        # =========================
        # ЕСТЬ ПОЗИЦИЯ
        # =========================
        elif position:

            avg_price = position["entry"]

            # =========================
            # ДОКУПКА
            # =========================
            if position["second_entry"] is None:
                drop = percent_change(position["entry"], price)

                if drop <= SECOND_DIP and (is_stable() or bounce_detected()):

                    position["second_entry"] = price
                    position["amount"] += TRADE_AMOUNT * 0.5

                    avg_price = (position["entry"] + price) / 2

                    send(f"🟡 BUY 2: {price}")
                    print("BUY 2")

            # =========================
            # ПЕРЕСЧЁТ СРЕДНЕЙ
            # =========================
            if position["second_entry"]:
                avg_price = (position["entry"] + position["second_entry"]) / 2

            profit = percent_change(avg_price, price)

            # =========================
            # TAKE PROFIT
            # =========================
            if profit >= TAKE_PROFIT:
                send(f"✅ SELL (TP): {price} | profit: {round(profit*100,2)}%")
                print("SELL TP")

                position = None
                cooldown_until = time.time() + COOLDOWN

            # =========================
            # STOP LOSS
            # =========================
            elif profit <= -STOP_LOSS:
                send(f"❌ SELL (SL): {price} | loss: {round(profit*100,2)}%")
print("SELL SL")

                position = None
                cooldown_until = time.time() + COOLDOWN

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

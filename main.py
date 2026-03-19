import time
import requests
from collections import deque

# =========================
# НАСТРОЙКИ
# =========================
SYMBOL = "BTCUSDT"

TRADE_AMOUNT = 100
TAKE_PROFIT = 0.025
STOP_LOSS = 0.025
DIP_THRESHOLD = -0.05
SECOND_DIP = -0.03

COOLDOWN = 900

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
# PRICE
# =========================
def get_price():
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}"
    return float(requests.get(url).json()["price"])

# =========================
# STATE
# =========================
prices = deque(maxlen=50)

position = None
cooldown_until = 0

# =========================
# HELPERS
# =========================
def percent_change(old, new):
    return (new - old) / old

def is_stable():
    if len(prices) < 6:
        return False
    last = list(prices)[-6:]
    return min(last[:-1]) <= last[-1]

def bounce_detected():
    if len(prices) < 3:
        return False
    return prices[-1] > prices[-2] > prices[-3]

def btc_market_ok():
    if len(prices) < 12:
        return True
    change = percent_change(prices[-12], prices[-1])
    return change > -0.05

# =========================
# MAIN LOOP
# =========================
print("BOT STARTED")

while True:
    try:
        price = get_price()
        prices.append(price)

        print(f"PRICE: {price}")

        # =========================
        # NO POSITION → ENTRY
        # =========================
        if position is None and time.time() > cooldown_until:

            if len(prices) > 10:
                change = percent_change(prices[0], price)

                if change <= DIP_THRESHOLD and btc_market_ok():

                    if is_stable() or bounce_detected():

                        position = {
                            "entry": price,
                            "second_entry": None
                        }

                        send(f"🟢 BUY 1: {price}")
                        print("BUY 1")

        # =========================
        # POSITION OPEN
        # =========================
        elif position:

            avg_price = position["entry"]

            # =========================
            # SECOND BUY
            # =========================
            if position["second_entry"] is None:
                drop = percent_change(position["entry"], price)

                if drop <= SECOND_DIP and (is_stable() or bounce_detected()):

                    position["second_entry"] = price
                    avg_price = (position["entry"] + price) / 2

                    send(f"🟡 BUY 2: {price}")
                    print("BUY 2")

            # =========================
            # AVG PRICE
            # =========================
            if position["second_entry"]:
                avg_price = (position["entry"] + position["second_entry"]) / 2

            profit = percent_change(avg_price, price)

            # =========================
            # TAKE PROFIT
            # =========================
            if profit >= TAKE_PROFIT:
                send(f"✅ SELL TP: {price} | {round(profit*100,2)}%")
                print("SELL TP")

                position = None
                cooldown_until = time.time() + COOLDOWN

            # =========================
            # STOP LOSS
            # =========================
            elif profit <= -STOP_LOSS:
                send(f"❌ SELL SL: {price} | {round(profit*100,2)}%")
                print("SELL SL")

                position = None
                cooldown_until = time.time() + COOLDOWN

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

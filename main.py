import time
import requests
from collections import deque
from binance.client import Client

# =========================
# BINANCE TESTNET
# =========================
API_KEY = "eCWy1i5O1Lh1pcUQwHNVeXSTPF6iAvJAEzD0MCun050Sq6jZyWDlFbbQjPX2e73w"
API_SECRET = "kkiygYBvpMADFOTNwbDFV3kv65HsvonOXqwRuSDZLf4GlHYwyaSQjh7zDBHRY4tZ"

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

SYMBOL = "BTCUSDT"

TAKE_PROFIT = 0.025
STOP_LOSS = 0.025

DIP_THRESHOLD = -0.03
SECOND_DIP = -0.025

COOLDOWN = 300

# =========================
# P2P НАСТРОЙКИ
# =========================
SPREAD_MIN = 0.4
SPREAD_MAX = 3.0

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
# HELPERS
# =========================
def get_price():
    return float(client.get_symbol_ticker(symbol=SYMBOL)["price"])

def get_balance(asset="USDT"):
    return float(client.get_asset_balance(asset=asset)["free"])

def percent_change(old, new):
    return (new - old) / old

# =========================
# P2P SCANNER
# =========================
def get_binance_p2p():
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    data = {
        "asset": "USDT",
        "fiat": "EUR",
        "tradeType": "SELL",
        "page": 1,
        "rows": 5,
        "payTypes": ["SEPA"]
    }

    res = requests.post(url, json=data).json()
    offers = res.get("data", [])

    valid = []
    for o in offers:
        adv = o["adv"]
        advertiser = o["advertiser"]

        if advertiser["monthOrderCount"] >= 99:
            valid.append(float(adv["price"]))

    return min(valid) if valid else None


def get_bybit_p2p():
    url = "https://api2.bybit.com/fiat/otc/item/online"
    data = {
        "tokenId": "USDT",
        "currencyId": "EUR",
        "side": "0",
        "page": 1,
        "size": 5
    }

    res = requests.post(url, json=data).json()
    offers = res.get("result", {}).get("items", [])

    valid = []
    for o in offers:
        if o["recentExecuteRate"] >= 99:
            valid.append(float(o["price"]))

    return max(valid) if valid else None


def check_p2p():
    try:
        binance_price = get_binance_p2p()
        bybit_price = get_bybit_p2p()

        if not binance_price or not bybit_price:
            return

        spread = (binance_price - bybit_price) / bybit_price * 100

        if SPREAD_MIN <= spread <= SPREAD_MAX:
            send(f"""
💰 P2P СВЯЗКА

Buy Bybit: {bybit_price}
Sell Binance: {binance_price}

Спред: {round(spread,2)}%
""")

    except Exception as e:
        print("P2P ERROR:", e)

# =========================
# STATE
# =========================
prices = deque(maxlen=50)

position = None
cooldown_until = 0

# =========================
# LOGIC
# =========================
def is_stable():
    if len(prices) < 6:
        return False
    last = list(prices)[-6:]
    return all(last[i] >= last[i-1] for i in range(1, len(last)))

def bounce_detected():
    if len(prices) < 3:
        return False
    return prices[-1] > prices[-2] > prices[-3]

def trend_ok():
    if len(prices) < 20:
        return True
    avg = sum(list(prices)[-20:]) / 20
    return prices[-1] > avg

def market_safe():
    if len(prices) < 20:
        return True
    return percent_change(prices[-20], prices[-1]) > -0.04

# =========================
# MAIN
# =========================
print("🚀 TESTNET BOT STARTED")
send("🚀 TESTNET BOT STARTED")

last_p2p_check = 0

while True:
    try:
        price = get_price()
        prices.append(price)

        print(f"PRICE: {price}")

        # =========================
        # P2P CHECK (раз в 60 сек)
        # =========================
        if time.time() - last_p2p_check > 60:
            check_p2p()
            last_p2p_check = time.time()

        # =========================
        # ENTRY
        # =========================
        if position is None and time.time() > cooldown_until:

            if len(prices) > 10:
                change = percent_change(prices[0], price)

                if change <= DIP_THRESHOLD and trend_ok() and market_safe():

                    if is_stable() or bounce_detected():

                        usdt = get_balance("USDT")
                        trade_amount = usdt * 0.2
                        qty = round(trade_amount / price, 6)

                        client.order_market_buy(
                            symbol=SYMBOL,
                            quantity=qty
                        )

                        position = {
                            "entry": price,
                            "qty": qty,
                            "second": False
                        }

                        send(f"""
🟢 BUY 1
Price: {price}
Qty: {qty}
USDT: {usdt}
""")

        # =========================
        # POSITION
        # =========================
        elif position:

            avg_price = position["entry"]

            if not position["second"]:
                drop = percent_change(position["entry"], price)

                if drop <= SECOND_DIP and (is_stable() or bounce_detected()):

                    usdt = get_balance("USDT")
                    trade_amount = usdt * 0.2
                    qty = round(trade_amount / price, 6)

                    client.order_market_buy(
                        symbol=SYMBOL,
                        quantity=qty
                    )

                    position["qty"] += qty
                    position["entry"] = (avg_price + price) / 2
                    position["second"] = True

                    send(f"🟡 BUY 2 {price}")

            profit = percent_change(avg_price, price)

            if profit >= TAKE_PROFIT:

                client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=round(position["qty"], 6)
                )

                send(f"""
✅ SELL TP
Price: {price}
Profit: {round(profit*100,2)}%
""")

                position = None
                cooldown_until = time.time() + COOLDOWN

            elif profit <= -STOP_LOSS:

                client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=round(position["qty"], 6)
                )

                send(f"""
❌ SELL SL
Price: {price}
Loss: {round(profit*100,2)}%
""")

                position = None
                cooldown_until = time.time() + COOLDOWN

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

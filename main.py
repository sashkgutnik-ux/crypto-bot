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
# PROXY (BYBIT FIX)
# =========================
PROXY = {
    "http": "http://ubibwgwk:7p0sy6uw77ga@31.59.20.176:6754",
    "https": "http://ubibwgwk:7p0sy6uw77ga@31.59.20.176:6754"
}

# =========================
# P2P SETTINGS
# =========================
SPREAD_MIN = -3.0
SPREAD_MAX = 3.0

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
# P2P BINANCE
# =========================
def get_binance_p2p():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        data = {
            "asset": "USDT",
            "fiat": "EUR",
            "tradeType": "SELL",
            "page": 1,
            "rows": 10,
            "payTypes": ["SEPA"]
        }

        res = requests.post(url, json=data, timeout=10).json()
        offers = res.get("data", [])

        valid = []
        for o in offers:
            adv = o["adv"]
            advertiser = o["advertiser"]

            if advertiser["monthOrderCount"] >= 99:
                valid.append(float(adv["price"]))

        return min(valid) if valid else None

    except:
        return None

# =========================
# P2P BYBIT (через прокси)
# =========================
def get_bybit_p2p():
    try:
        url = "https://api2.bybit.com/fiat/otc/item/online"
        data = {
            "tokenId": "USDT",
            "currencyId": "EUR",
            "side": "0",
            "page": 1,
            "size": 10
        }

        res = requests.post(url, json=data, proxies=PROXY, timeout=10).json()
        offers = res.get("result", {}).get("items", [])

        valid = []
        for o in offers:
            if float(o["recentExecuteRate"]) >= 99:
                valid.append(float(o["price"]))

        return max(valid) if valid else None

    except Exception as e:
        print("BYBIT ERROR:", e)
        return None

# =========================
# P2P CHECK
# =========================
def check_p2p():
    b_price = get_binance_p2p()
    y_price = get_bybit_p2p()

    print("DEBUG:", b_price, y_price)

    if not b_price or not y_price:
        print("P2P NO DATA")
        return

    spread = (b_price - y_price) / y_price * 100

    msg = f"""
💰 P2P

Bybit BUY: {y_price}
Binance SELL: {b_price}

Spread: {round(spread,2)}%
"""

    print(msg)

    if SPREAD_MIN <= spread <= SPREAD_MAX:
        send(msg)

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
print("🚀 BOT STARTED")
send("🚀 BOT STARTED")

last_p2p = 0

while True:
    try:
        price = get_price()
        prices.append(price)

        print(f"PRICE: {price}")

        # P2P каждые 10 сек
        if time.time() - last_p2p > 10:
            check_p2p()
            last_p2p = time.time()

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

                        send(f"🟢 BUY {price}")

        # =========================
        # POSITION
        # =========================
        elif position:

            avg_price = position["entry"]
            profit = percent_change(avg_price, price)

            if profit >= TAKE_PROFIT:
                client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=round(position["qty"], 6)
                )

                send(f"✅ SELL TP {round(profit*100,2)}%")
                position = None
                cooldown_until = time.time() + COOLDOWN

            elif profit <= -STOP_LOSS:
                client.order_market_sell(
                    symbol=SYMBOL,
                    quantity=round(position["qty"], 6)
                )

                send(f"❌ SELL SL {round(profit*100,2)}%")
                position = None
                cooldown_until = time.time() + COOLDOWN

        time.sleep(5)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

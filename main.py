import time
import requests
from binance.client import Client

# =========================
# BINANCE TESTNET API
# =========================
API_KEY = "eCWy1i5O1Lh1pcUQwHNVeXSTPF6iAvJAEzD0MCun050Sq6jZyWDlFbbQjPX2e73w"
API_SECRET = "kkiygYBvpMADFOTNwbDFV3kv65HsvonOXqwRuSDZLf4GlHYwyaSQjh7zDBHRY4tZ"

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

# =========================
# TELEGRAM
# =========================
BOT_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = 8039241406

def send(msg):
    try:
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print("TG ERROR:", e)

# =========================
# SETTINGS
# =========================
SYMBOL = "BTCUSDT"
QTY = 0.001

TAKE_PROFIT = 0.02
STOP_LOSS = 0.02

entry_price = None

# =========================
# FUNCTIONS
# =========================
def get_price():
    return float(client.get_symbol_ticker(symbol=SYMBOL)["price"])

def buy():
    return client.order_market_buy(symbol=SYMBOL, quantity=QTY)

def sell():
    return client.order_market_sell(symbol=SYMBOL, quantity=QTY)

# =========================
# START
# =========================
print("BOT STARTED")
send("🚀 TESTNET BOT STARTED")

# =========================
# LOOP
# =========================
while True:
    try:
        price = get_price()
        print("PRICE:", price)

        if entry_price is None:
            buy()
            entry_price = price
            send(f"🟢 BUY {price}")

        else:
            change = (price - entry_price) / entry_price

            if change >= TAKE_PROFIT:
                sell()
                send(f"✅ SELL TP {price}")
                entry_price = None

            elif change <= -STOP_LOSS:
                sell()
                send(f"❌ SELL SL {price}")
                entry_price = None

        time.sleep(10)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(5)

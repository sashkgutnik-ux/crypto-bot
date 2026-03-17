mport time
import requests
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

# ===== SETTINGS =====
SYMBOL = "BTCUSDC"
SLEEP = 15

RISK = 0.15
STOP_LOSS = 0.01
TAKE_PROFIT = 0.02
TRAILING_STOP = 0.008

# Telegram
TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

in_position = False
entry_price = 0
highest_price = 0
last_trade_time = 0


# ===== TELEGRAM =====
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# ===== POSITION SIZE =====
def position_size(balance, price):
    return round((balance * RISK) / price, 6)


# ===== MAIN =====
def run():
    global in_position, entry_price, highest_price, last_trade_time

    client = BinanceClient()

    while True:
        try:
            prices = get_historical_prices(SYMBOL)
            price = prices[-1]

            ema50 = calculate_ema(prices, 50)
            ema200 = calculate_ema(prices, 200)
            rsi = calculate_rsi(prices)

            print("\nPRICE:", price)
            print("EMA50:", ema50, "EMA200:", ema200, "RSI:", rsi)

            signal = "HOLD"

            # 🔥 УМНАЯ СТРАТЕГИЯ
            trend_up = ema50 > ema200
            trend_down = ema50 < ema200

            # фильтр флета
            trend_strength = abs(ema50 - ema200) / price

            if trend_up and rsi < 48 and trend_strength > 0.001:
                signal = "BUY"

            elif trend_down and rsi > 52 and trend_strength > 0.001:
                signal = "SELL"

            print("Signal:", signal)

            usdc = client.get_balance("USDC")
            btc = client.get_balance("BTC")

            print("USDC:", usdc, "BTC:", btc)

            now = time.time()

            # ===== BUY =====
            if signal == "BUY" and not in_position and usdc > 5 and now - last_trade_time > 60:

                qty = max(position_size(usdc, price), 0.00001)

                print("🟢 BUY BTC")
                client.buy(SYMBOL, qty)

                send_telegram(f"🟢 BUY BTC\nPrice: {price}\nQty: {qty}")

                entry_price = price
                highest_price = price
                in_position = True
                last_trade_time = now

            # ===== SELL SIGNAL =====
            elif signal == "SELL" and in_position and btc > 0.00001:

                print("🔴 SELL BTC")
                client.sell(SYMBOL, btc)

                send_telegram(f"🔴 SELL BTC\nPrice: {price}")

                in_position = False
                last_trade_time = now

            # ===== POSITION MGMT =====
            if in_position:
                highest_price = max(highest_price, price)

                # STOP LOSS
                if price <= entry_price * (1 - STOP_LOSS):
                    print("🛑 STOP LOSS")
                    client.sell(SYMBOL, btc)

                    send_telegram(f"🛑 STOP LOSS\nPrice: {price}")

                    in_position = False

                # TAKE PROFIT
                elif price >= entry_price * (1 + TAKE_PROFIT):
                    print("💰 TAKE PROFIT")
                    client.sell(SYMBOL, btc)

                    send_telegram(f"💰 TAKE PROFIT\nPrice: {price}")

                    in_position = False

                # TRAILING
                elif price <= highest_price * (1 - TRAILING_STOP):
                    print("📉 TRAILING STOP")
                    client.sell(SYMBOL, btc)

                    send_telegram(f"📉 TRAILING STOP\nPrice: {price}")

                    in_position = False

            time.sleep(SLEEP)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(SLEEP)


if __name__ == "__main__":
    print("🚀 BOT WITH TELEGRAM STARTED")
    send_telegram("🤖 Bot started")
    run()

import time
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

# ===== SETTINGS =====
SYMBOL = "BTCUSDC"
SLEEP = 15

RISK = 0.2          # 20% от баланса в сделку (для маленького депозита)
STOP_LOSS = 0.01    # 1%
TAKE_PROFIT = 0.015 # 1.5%

in_position = False
entry_price = 0


# ===== POSITION SIZE =====
def position_size(balance, price):
    return round((balance * RISK) / price, 6)


# ===== MAIN LOOP =====
def run():
    global in_position, entry_price

    client = BinanceClient()

    while True:
        try:
            prices = get_historical_prices(SYMBOL)
            price = prices[-1]

            ema50 = calculate_ema(prices, 50)
            ema200 = calculate_ema(prices, 200)
            rsi = calculate_rsi(prices)

            print("\n===== MARKET =====")
            print("PRICE:", price)

            print("\n===== INDICATORS =====")
            print("EMA50:", ema50)
            print("EMA200:", ema200)
            print("RSI:", rsi)

            # ===== SIGNAL =====
            signal = "HOLD"

            # 🔥 улучшенные входы (чаще сделки)
            if ema50 > ema200 and rsi < 45:
                signal = "BUY"
            elif ema50 < ema200 and rsi > 55:
                signal = "SELL"

            print("\nSignal:", signal)

            # ===== BALANCE =====
            usdc = client.get_balance("USDC")
            btc = client.get_balance("BTC")

            print("\n===== BALANCE =====")
            print("USDC:", usdc)
            print("BTC:", btc)

            # ===== BUY =====
            if signal == "BUY" and not in_position and usdc > 5:
                qty = max(position_size(usdc, price), 0.00001)

                print("\n🟢 BUY BTC:", qty)
                client.buy(SYMBOL, qty)

                entry_price = price
                in_position = True

            # ===== SELL (signal) =====
            elif signal == "SELL" and in_position and btc > 0.00001:
                print("\n🔴 SELL BTC (signal)")
                client.sell(SYMBOL, btc)

                in_position = False

            # ===== POSITION MANAGEMENT =====
            if in_position:

                # 🛑 STOP LOSS
                if price <= entry_price * (1 - STOP_LOSS):
                    print("\n🛑 STOP LOSS TRIGGERED")
                    client.sell(SYMBOL, btc)
                    in_position = False

                # 💰 TAKE PROFIT
                elif price >= entry_price * (1 + TAKE_PROFIT):
                    print("\n💰 TAKE PROFIT")
                    client.sell(SYMBOL, btc)
                    in_position = False

            time.sleep(SLEEP)

        except Exception as e:
            print("\n❌ ERROR:", e)
            time.sleep(SLEEP)


# ===== START =====
if __name__ == "__main__":
    print("🚀 STARTING BOT (EMA + RSI + SL + TP)")
    run()

import time
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

SYMBOL = "BTCUSDC"
SLEEP = 15

RISK = 0.02  # 2%
STOP_LOSS = 0.01  # 1%

in_position = False
entry_price = 0


def position_size(balance, price):
    return round((balance * RISK) / price, 5)


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

            print("\nPRICE:", price)
            print("EMA50:", ema50, "EMA200:", ema200, "RSI:", rsi)

            signal = "HOLD"

            if ema50 > ema200 and rsi < 30:
                signal = "BUY"
            elif ema50 < ema200 and rsi > 70:
                signal = "SELL"

            print("Signal:", signal)

            usdc = client.get_balance("USDC")
            btc = client.get_balance("BTC")

            print("USDC:", usdc, "BTC:", btc)

            # ===== BUY =====
            if signal == "BUY" and not in_position and usdc > 10:
                qty = max(position_size(usdc, price), 0.0001)

                print("🟢 BUY BTC")
                client.buy(SYMBOL, qty)

                entry_price = price
                in_position = True

            # ===== SELL =====
            elif signal == "SELL" and in_position and btc > 0.00001:
                print("🔴 SELL BTC")
                client.sell(SYMBOL, btc)

                in_position = False

            # ===== STOP LOSS =====
            if in_position:
                if price <= entry_price * (1 - STOP_LOSS):
                    print("🛑 STOP LOSS TRIGGERED")
                    client.sell(SYMBOL, btc)
                    in_position = False

            time.sleep(SLEEP)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(SLEEP)


if __name__ == "__main__":
    run()

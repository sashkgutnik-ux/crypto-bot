import time
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

SYMBOL = "BTCUSDT"
SLEEP = 10

LEVERAGE = 2
RISK = 0.1        # 10% от баланса
STOP_LOSS = 0.01  # 1%
TAKE_PROFIT = 0.02 # 2%

in_position = False
entry_price = 0
side = None


def position_size(balance, price):
    return round((balance * RISK * LEVERAGE) / price, 3)


def run():
    global in_position, entry_price, side

    client = BinanceClient()
    client.set_leverage(SYMBOL, LEVERAGE)

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

            # 🔥 ЛОНГ
            if ema50 > ema200 and rsi < 45:
                signal = "LONG"

            # 🔥 ШОРТ
            elif ema50 < ema200 and rsi > 55:
                signal = "SHORT"

            print("Signal:", signal)

            balance = client.get_balance()
            print("USDT Futures:", balance)

            qty = position_size(balance, price)

            # ===== ENTRY =====
            if not in_position and signal == "LONG":
                print("🟢 OPEN LONG")
                client.order(SYMBOL, "BUY", qty)

                entry_price = price
                side = "BUY"
                in_position = True

            elif not in_position and signal == "SHORT":
                print("🔴 OPEN SHORT")
                client.order(SYMBOL, "SELL", qty)

                entry_price = price
                side = "SELL"
                in_position = True

            # ===== EXIT =====
            if in_position:

                # STOP LOSS
                if side == "BUY" and price <= entry_price * (1 - STOP_LOSS):
                    print("🛑 SL LONG")
                    client.close_position(SYMBOL, side, qty)
                    in_position = False

                elif side == "SELL" and price >= entry_price * (1 + STOP_LOSS):
                    print("🛑 SL SHORT")
                    client.close_position(SYMBOL, side, qty)
                    in_position = False

                # TAKE PROFIT
                elif side == "BUY" and price >= entry_price * (1 + TAKE_PROFIT):
                    print("💰 TP LONG")
                    client.close_position(SYMBOL, side, qty)
                    in_position = False

                elif side == "SELL" and price <= entry_price * (1 - TAKE_PROFIT):
                    print("💰 TP SHORT")
                    client.close_position(SYMBOL, side, qty)
                    in_position = False

            time.sleep(SLEEP)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(SLEEP)


if __name__ == "__main__":
    print("🚀 FUTURES BOT STARTED")
    run()

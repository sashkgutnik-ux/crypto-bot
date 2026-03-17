import time
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

SYMBOL = "BTCUSDT"
SLEEP = 15

RISK = 0.02
SL = 0.01


def size(balance, price):
    return round((balance * RISK) / price, 5)


def run():
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

            usdt = client.get_balance("USDT")
            btc = client.get_balance("BTC")

            print("USDT:", usdt, "BTC:", btc)

            if usdt < 10:
                print("❌ Not enough balance")
                time.sleep(SLEEP)
                continue

            # делим баланс
            spot_balance = usdt / 2
            futures_balance = usdt / 2

            qty_spot = size(spot_balance, price)
            qty_fut = size(futures_balance, price)

            # ===== SPOT =====
            if signal == "BUY" and spot_balance > 10:
                print("🟢 SPOT BUY")
                client.spot_buy(SYMBOL, qty_spot)

            elif signal == "SELL" and btc > 0.0001:
                print("🔴 SPOT SELL")
                client.spot_sell(SYMBOL, btc)

            # ===== FUTURES =====
            pos = client.get_position(SYMBOL)

            if pos == 0:
                if signal == "BUY":
                    print("🟢 FUTURES LONG")
                    client.futures_order(SYMBOL, "BUY", qty_fut)

                    sl_price = price * (1 - SL)
                    client.set_stop_loss(SYMBOL, "BUY", sl_price)

                elif signal == "SELL":
                    print("🔴 FUTURES SHORT")
                    client.futures_order(SYMBOL, "SELL", qty_fut)

                    sl_price = price * (1 + SL)
                    client.set_stop_loss(SYMBOL, "SELL", sl_price)

            else:
                print("⛔ Futures position exists")

            time.sleep(SLEEP)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(SLEEP)


if __name__ == "__main__":
    run()

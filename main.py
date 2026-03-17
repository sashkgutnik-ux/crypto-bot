import time
from binance_client import BinanceClient
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

SYMBOL = "BTCUSDT"
SLEEP = 10

RISK_PERCENT = 0.01  # 1% риск
STOP_LOSS_PERCENT = 0.01  # 1%
TAKE_PROFIT_PERCENT = 0.02  # 2%


def calculate_position_size(balance, price):
    risk_amount = balance * RISK_PERCENT
    quantity = risk_amount / price
    return round(quantity, 5)


def run_bot():
    client = BinanceClient()

    while True:
        try:
            prices = get_historical_prices(SYMBOL)
            current_price = prices[-1]

            ema50 = calculate_ema(prices, 50)
            ema200 = calculate_ema(prices, 200)
            rsi = calculate_rsi(prices)

            print("\n===== MARKET DATA =====")
            print(f"BTC price: {current_price}")

            print("\n===== INDICATORS =====")
            print(f"EMA50: {ema50}")
            print(f"EMA200: {ema200}")
            print(f"RSI: {rsi}")

            signal = "HOLD"

            if ema50 > ema200 and rsi < 30:
                signal = "BUY"
            elif ema50 < ema200 and rsi > 70:
                signal = "SELL"

            print(f"Signal: {signal}")

            balance = client.get_balance("USDT")
            print(f"\nBalance USDT: {balance}")

            if balance == 0:
                print("No balance → skip")
                time.sleep(SLEEP)
                continue

            qty = calculate_position_size(balance, current_price)

            # === FUTURES TRADING ===
            if signal == "BUY":
                print("Opening LONG")

                entry = current_price
                sl = entry * (1 - STOP_LOSS_PERCENT)
                tp = entry * (1 + TAKE_PROFIT_PERCENT)

                client.open_futures_position(
                    symbol=SYMBOL,
                    side="BUY",
                    quantity=qty
                )

                print(f"SL: {sl}, TP: {tp}")

            elif signal == "SELL":
                print("Opening SHORT")

                entry = current_price
                sl = entry * (1 + STOP_LOSS_PERCENT)
                tp = entry * (1 - TAKE_PROFIT_PERCENT)

                client.open_futures_position(
                    symbol=SYMBOL,
                    side="SELL",
                    quantity=qty
                )

                print(f"SL: {sl}, TP: {tp}")

            else:
                print("No trade")

            time.sleep(SLEEP)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(SLEEP)


if __name__ == "__main__":
    run_bot()

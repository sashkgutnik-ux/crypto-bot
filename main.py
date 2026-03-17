import time
from price_history import get_historical_prices
from indicators import calculate_ema, calculate_rsi
from binance_client import BinanceClient

SYMBOL = "BTCUSDT"
SLEEP = 30  # секунд между циклами

# риск-менеджмент
RISK_PER_TRADE = 0.02  # 2% от депозита
TAKE_PROFIT = 0.02     # 2%
STOP_LOSS = 0.01       # 1%


client = BinanceClient()


def get_signal(prices):
    ema50 = calculate_ema(prices, 50)
    ema200 = calculate_ema(prices, 200)
    rsi = calculate_rsi(prices)

    print("\n===== INDICATORS =====")
    print(f"EMA50: {ema50}")
    print(f"EMA200: {ema200}")
    print(f"RSI: {rsi}")

    # стратегия
    if ema50 > ema200 and rsi < 35:
        return "BUY"
    elif ema50 < ema200 and rsi > 65:
        return "SELL"
    else:
        return "HOLD"


def calculate_position_size(usdt_balance, price):
    risk_amount = usdt_balance * RISK_PER_TRADE
    quantity = risk_amount / price
    return round(quantity, 6)


def run_bot():
    print("🚀 Starting REAL Trading Bot (EMA + RSI)")

    while True:
        try:
            prices = get_historical_prices(SYMBOL)
            current_price = prices[-1]

            print("\n===== MARKET DATA =====")
            print(f"BTC price: {current_price}")

            signal = get_signal(prices)
            print(f"Signal: {signal}")

            # баланс
            usdt_balance = client.get_balance("USDT")
            btc_balance = client.get_balance("BTC")

            print("\n===== BALANCE =====")
            print(f"USDT: {usdt_balance}")
            print(f"BTC: {btc_balance}")

            # позиция
            qty = calculate_position_size(usdt_balance, current_price)

            # ===== ТОРГОВЛЯ =====
            if signal == "BUY" and usdt_balance > 10:
                print(f"🟢 BUY {qty} BTC")

                client.market_buy(SYMBOL, qty)

                tp_price = current_price * (1 + TAKE_PROFIT)
                sl_price = current_price * (1 - STOP_LOSS)

                print(f"TP: {tp_price} | SL: {sl_price}")

            elif signal == "SELL" and btc_balance > 0.0001:
                print(f"🔴 SELL {qty} BTC")

                client.market_sell(SYMBOL, qty)

            else:
                print("No trade")

        except Exception as e:
            print(f"❌ ERROR: {e}")

        time.sleep(SLEEP)


if __name__ == "__main__":
    run_bot()

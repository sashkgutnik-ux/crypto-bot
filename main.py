import time
from binance_client import get_price, market_buy, market_sell, get_balance
from indicators import calculate_ema, calculate_rsi
from price_history import get_historical_prices

SYMBOL = "BTCUSDT"

# === НАСТРОЙКИ ===
RISK_PER_TRADE = 0.05   # 5% депозита
STOP_LOSS = 0.97        # -3%
TAKE_PROFIT = 1.03      # +3%

EMA_FAST = 50
EMA_SLOW = 200

RSI_PERIOD = 14

in_position = False
entry_price = 0


def check_signal(prices):
    ema_fast = calculate_ema(prices, EMA_FAST)
    ema_slow = calculate_ema(prices, EMA_SLOW)
    rsi = calculate_rsi(prices, RSI_PERIOD)

    print("\n===== INDICATORS =====")
    print(f"EMA{EMA_FAST}: {ema_fast}")
    print(f"EMA{EMA_SLOW}: {ema_slow}")
    print(f"RSI: {rsi}")

    # === ЛОГИКА ===
    if ema_fast > ema_slow and rsi < 30:
        return "BUY"

    elif ema_fast < ema_slow and rsi > 70:
        return "SELL"

    return "HOLD"


def calculate_position_size(usdt_balance, price):
    amount_usdt = usdt_balance * RISK_PER_TRADE
    btc_amount = amount_usdt / price
    return round(btc_amount, 6)


def run_bot():
    global in_position, entry_price

    print("🚀 Starting REAL Trading Bot (EMA + RSI)")

    while True:
        try:
            price = get_price(SYMBOL)
            prices = get_historical_prices(SYMBOL)

            print("\n===== MARKET DATA =====")
            print(f"BTC price: {price}")

            signal = check_signal(prices)
            print(f"Signal: {signal}")

            usdt, btc = get_balance()

            print("\n===== BALANCE =====")
            print(f"USDT: {usdt}")
            print(f"BTC: {btc}")

            # === ЕСЛИ НЕ В ПОЗИЦИИ ===
            if not in_position:

                if signal == "BUY":
                    amount = calculate_position_size(usdt, price)

                    print(f"\n🟢 BUY {amount} BTC")

                    market_buy(SYMBOL, amount)

                    entry_price = price
                    in_position = True

            # === ЕСЛИ В ПОЗИЦИИ ===
            else:
                print(f"\n📊 In position at {entry_price}")

                # STOP LOSS
                if price <= entry_price * STOP_LOSS:
                    print("🔴 STOP LOSS")
                    market_sell(SYMBOL, btc)
                    in_position = False

                # TAKE PROFIT
                elif price >= entry_price * TAKE_PROFIT:
                    print("🟢 TAKE PROFIT")
                    market_sell(SYMBOL, btc)
                    in_position = False

                # SIGNAL SELL (по стратегии)
                elif signal == "SELL":
                    print("⚠️ Strategy SELL")
                    market_sell(SYMBOL, btc)
                    in_position = False

            time.sleep(10)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            time.sleep(10)


if __name__ == "__main__":
    run_bot()

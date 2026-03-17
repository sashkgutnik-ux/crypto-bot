import time

from ai_strategy_selector import choose_best_strategy
import trading_strategies

from binance_client import (
    market_buy,
    market_sell,
    get_balance,
    get_price,
)

SYMBOL = "BTCUSDT"
RISK = 0.05
SLEEP = 5


# ===== Получение сигнала =====
def get_signal(strategy, price):
    try:
        if strategy == "EMA":
            return trading_strategies.ema_strategy(price)

        elif strategy == "RSI":
            return trading_strategies.rsi_strategy(price)

        elif strategy == "Breakout":
            return trading_strategies.breakout_strategy(price)

        elif strategy == "Bollinger":
            return trading_strategies.bollinger_strategy(price)

        elif strategy == "Grid":
            return trading_strategies.grid_strategy(price)

    except Exception as e:
        print(f"{strategy} error: {e}")

    return "HOLD"


# ===== БОТ =====
def run_bot():
    print("🚀 AI Trading Bot (SCORING MODE)")

    in_position = False

    while True:
        price = get_price(SYMBOL)

        print("\n===== MARKET DATA =====")
        print(f"BTC price: {price}")

        # ===== AI =====
        try:
            ai_result = choose_best_strategy(price)
        except Exception as e:
            print(f"AI error: {e}")
            continue

        print("===== AI SCORES (%) =====")
        for k, v in ai_result.items():
            print(f"{k}: {v}%")

        # ===== ЛУЧШАЯ СТРАТЕГИЯ =====
        best_strategy = max(ai_result, key=ai_result.get)
        best_score = ai_result[best_strategy]

        print(f"\nBEST STRATEGY: {best_strategy} ({best_score}%)")

        # фильтр — не торгуем если слабый сигнал
        if best_score < 25:
            print("Signal too weak → SKIP")
            time.sleep(SLEEP)
            continue

        signal = get_signal(best_strategy, price)
        print(f"Signal: {signal}")

        # ===== БАЛАНС =====
        usdt = get_balance("USDT")
        btc = get_balance("BTC")

        trade_amount = usdt * RISK

        print("\n===== BALANCE =====")
        print(f"USDT: {usdt}")
        print(f"BTC: {btc}")

        # ===== ТОРГОВЛЯ =====
        try:
            if signal == "BUY" and not in_position:
                print("🟢 BUY")
                market_buy(SYMBOL, trade_amount)
                in_position = True

            elif signal == "SELL" and in_position and btc > 0:
                print("🔴 SELL")
                market_sell(SYMBOL, btc)
                in_position = False

            else:
                print("No trade")

        except Exception as e:
            print(f"Trade error: {e}")

        time.sleep(SLEEP)


if __name__ == "__main__":
    run_bot()

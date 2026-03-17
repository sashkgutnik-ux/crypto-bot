import time

from ai_strategy_selector import choose_best_strategy
import trading_strategies

from binance_client import market_buy, market_sell, print_balance, get_price


def run_bot():
    print("🚀 Starting AI Trading Bot (BINANCE MODE)")

    while True:
        price = get_price()

        print("\n===== MARKET DATA =====")
        print(f"BTC price: {price}")

        # AI
        try:
            ai_result = choose_best_strategy(price)[0]
        except:
            ai_result = choose_best_strategy(price)

        print("===== AI ANALYSIS =====")
        for k, v in ai_result.items():
            print(f"{k}: {v}")

        # выбор стратегии
        best_strategy = max(ai_result, key=ai_result.get)
        print(f"\nBEST STRATEGY: {best_strategy}")

        signal = "HOLD"

        try:
            if best_strategy == "EMA":
                signal = trading_strategies.ema_strategy(price)

            elif best_strategy == "RSI":
                signal = trading_strategies.rsi_strategy(price)

            elif best_strategy == "Breakout":
                signal = trading_strategies.breakout_strategy(price)

            elif best_strategy == "Bollinger":
                signal = trading_strategies.bollinger_strategy(price)

            elif best_strategy == "Grid":
                signal = trading_strategies.grid_strategy(price)

        except Exception as e:
            print(f"Strategy error: {e}")

        print(f"Signal: {signal}")

        # ===== РЕАЛЬНАЯ ТОРГОВЛЯ =====
        try:
            if signal == "BUY":
                print("🟢 REAL BUY")
                market_buy("BTCUSDT", 50)  # покупка на 50 USDT

            elif signal == "SELL":
                print("🔴 REAL SELL")
                market_sell("BTCUSDT", 0.001)

        except Exception as e:
            print(f"Trade error: {e}")

        # баланс
        try:
            print_balance()
        except Exception as e:
            print(f"Balance error: {e}")

        time.sleep(5)


if __name__ == "__main__":
    run_bot()

import time
import requests

from ai_strategy_selector import choose_best_strategy
from paper_trader import PaperTrader
import trading_strategies


# ===== Получение цены BTC =====
def get_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        data = requests.get(url).json()
        return float(data["price"])
    except Exception as e:
        print("Ошибка получения цены:", e)
        return None


# ===== Основной запуск =====
def run_bot():
    print("🚀 Starting AI Trading Bot (Simulation Mode)")

    trader = PaperTrader(balance=1000)

    while True:
        print("\n===== MARKET DATA =====")

        price = get_price()
        if not price:
            continue

        print(f"BTC price: {price}")

        # AI выбор стратегии
        ai_result = choose_best_strategy(price)[0]

        print("\n===== AI ANALYSIS =====")
        for k, v in ai_result.items():
            print(f"{k}: {v}")

        best_strategy = max(ai_result, key=ai_result.get)
        print(f"\nBEST STRATEGY: {best_strategy}")

        # ===== Запуск стратегии =====
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

            else:
                signal = "HOLD"

            print(f"Signal: {signal}")

            # ===== Выполнение сделки =====
            if signal == "BUY":
                trader.buy(price, 100)

            elif signal == "SELL":
                trader.sell(price)

            print(f"Balance: {trader.balance}")
            print(f"Position: {trader.position}")

        except Exception as e:
            print("BOT ERROR:", e)

        time.sleep(5)


# ===== Запуск =====
if __name__ == "__main__":
    run_bot()

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
    except:
        return 0


# ===== Основной бот =====
def run_bot():
    print("🚀 Starting AI Trading Bot (Simulation Mode)")

    trader = PaperTrader()

    # 🔥 ФИКС если balance нет
    if not hasattr(trader, "balance"):
        trader.balance = 1000
        trader.btc = 0

    while True:
        price = get_price()

        print("\n===== MARKET DATA =====")
        print(f"BTC price: {price}")

        # AI выбор стратегии
        ai_result = choose_best_strategy(price)[0]

        print("===== AI ANALYSIS =====")
        for k, v in ai_result.items():
            print(f"{k}: {v}")

        # выбор лучшей стратегии
        best_strategy = max(ai_result, key=ai_result.get)
        print(f"\nBEST STRATEGY: {best_strategy}")

        # ===== СИГНАЛ =====
        signal = "HOLD"

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

        print(f"Signal: {signal}")

        # ===== ТОРГОВЛЯ =====
        try:
            if signal == "BUY":
                trader.buy(price, trader.balance * 0.1)

            elif signal == "SELL":
                trader.sell(price)

            trader.status()

        except Exception as e:
            print(f"BOT ERROR: {e}")

        time.sleep(5)


# ===== Запуск =====
if __name__ == "__main__":
    run_bot()

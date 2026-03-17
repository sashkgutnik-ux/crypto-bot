import time
import requests

from ai_strategy import choose_best_strategy
from simulation.paper_trader import PaperTrader

from strategy.trading_strategies import (
    ema_strategy,
    rsi_strategy,
    breakout_strategy,
    bollinger_strategy,
    grid_strategy
)


# ===== Получение цены BTC =====

def get_price():

    try:

        url = "https://api.coingecko.com/api/v3/simple/price"

        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd"
        }

        response = requests.get(url, params=params)

        data = response.json()

        return data["bitcoin"]["usd"]

    except:

        return 73000


# ===== Основной цикл =====

def main():

    print("🚀 Starting AI Trading Bot (Simulation Mode)")

    trader = PaperTrader(balance=1000)

    while True:

        try:

            price = get_price()

            print("\n===== MARKET DATA =====")
            print("BTC price:", price)

            market_data = {
                "btc_price": price
            }

            scores, best_strategy = choose_best_strategy(market_data)

            print("\n===== AI ANALYSIS =====")

            for name, value in scores.items():
                print(name, ":", value)

            print("\nBEST STRATEGY:", best_strategy)

            # ===== Запуск стратегии =====

            if best_strategy == "EMA":

                decision = ema_strategy(price)

            elif best_strategy == "RSI":

                decision = rsi_strategy(price)

            elif best_strategy == "Breakout":

                decision = breakout_strategy(price)

            elif best_strategy == "Bollinger":

                decision = bollinger_strategy(price)

            elif best_strategy == "Grid":

                decision = grid_strategy(price)

            else:

                decision = "hold"

            print("Decision:", decision)

            # ===== Симуляция сделки =====

            if decision == "buy":

                trader.buy(price, 100)

            elif decision == "sell":

                trader.sell(price)

            trader.status(price)

            time.sleep(10)

        except Exception as e:

            print("BOT ERROR:", e)
            time.sleep(5)


# ===== Запуск =====

if __name__ == "__main__":

    main()

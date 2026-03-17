from data.binance_history import load_btc_history
from core.price_history import add_price
from strategy.strategy_engine import analyze_price
from execution.trade_executor import execute_trade
from risk.stop_take import check_stop_take

total_profit = 0


def run_backtest(short_window=5, long_window=20):

    global total_profit

    position = None

    print("START BACKTEST")
    print("----------------------")

    prices = load_btc_history()

    print("Loaded candles:", len(prices))

    for price in prices:

        print("Price:", price)

        add_price(price)

        signal = analyze_price(price, short_window, long_window)

        print("Signal:", signal)

        execute_trade(signal, price)

        stop_signal = check_stop_take(position, price)

        if stop_signal == "STOP":
            print("STOP LOSS triggered")

        if stop_signal == "TAKE":
            print("TAKE PROFIT triggered")

    print("----------------------")
    print("BACKTEST FINISHED")
    print("Total profit:", round(total_profit, 2), "$")

    return total_profit

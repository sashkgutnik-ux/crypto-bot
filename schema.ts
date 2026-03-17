from backtest.backtester import run_backtest


def optimize_strategy():

    best_profit = -999999
    best_params = None

    short_range = range(5, 20)
    long_range = range(20, 60)

    print("STARTING OPTIMIZATION")

    for short_ma in short_range:
        for long_ma in long_range:

            if short_ma >= long_ma:
                continue

            profit = run_backtest(short_ma, long_ma)

            print(
                "short:", short_ma,
                "long:", long_ma,
                "profit:", round(profit, 2)
            )

            if profit > best_profit:
                best_profit = profit
                best_params = (short_ma, long_ma)

    print("\nBEST STRATEGY FOUND")

    print("Short MA:", best_params[0])
    print("Long MA:", best_params[1])
    print("Profit:", round(best_profit, 2))

    return best_params

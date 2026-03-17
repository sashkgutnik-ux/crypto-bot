def ema_strategy(price):
    return "BUY" if price % 2 == 0 else "SELL"


def rsi_strategy(price):
    return "BUY" if price < 75000 else "SELL"


def breakout_strategy(price):
    return "BUY" if price > 75500 else "SELL"


def bollinger_strategy(price):
    return "BUY" if price < 75200 else "SELL"


def grid_strategy(price):
    return "HOLD"

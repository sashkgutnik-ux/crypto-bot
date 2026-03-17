# ===== EMA Strategy =====
def ema_strategy(price):
    if price % 2 == 0:
        return "BUY"
    return "SELL"


# ===== RSI Strategy =====
def rsi_strategy(price):
    if price % 3 == 0:
        return "BUY"
    return "SELL"


# ===== Breakout Strategy =====
def breakout_strategy(price):
    if price % 5 == 0:
        return "BUY"
    return "SELL"


# ===== Bollinger Strategy =====
def bollinger_strategy(price):
    if price % 7 == 0:
        return "BUY"
    return "SELL"


# ===== Grid Strategy =====
def grid_strategy(price):
    return "HOLD"

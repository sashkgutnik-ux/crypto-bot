import random


def ema_strategy(price):

    if random.random() > 0.65:
        return "buy"

    if random.random() < 0.35:
        return "sell"

    return "hold"



def rsi_strategy(price):

    rsi = random.randint(20, 80)

    if rsi < 30:
        return "buy"

    if rsi > 70:
        return "sell"

    return "hold"



def breakout_strategy(price):

    if random.random() > 0.7:
        return "buy"

    if random.random() < 0.3:
        return "sell"

    return "hold"



def bollinger_strategy(price):

    if random.random() > 0.65:
        return "buy"

    if random.random() < 0.35:
        return "sell"

    return "hold"



def grid_strategy(price):

    if random.random() > 0.5:
        return "buy"

    return "sell"
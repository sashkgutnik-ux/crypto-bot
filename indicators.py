def check_stop_take(position, price, stop_loss=0.01, take_profit=0.02):

    if position is None:
        return None

    entry_price = position["entry_price"]
    side = position["side"]

    if side == "LONG":

        if price <= entry_price * (1 - stop_loss):
            return "STOP"

        if price >= entry_price * (1 + take_profit):
            return "TAKE"

    if side == "SHORT":

        if price >= entry_price * (1 + stop_loss):
            return "STOP"

        if price <= entry_price * (1 - take_profit):
            return "TAKE"

    return None
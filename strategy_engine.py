balance = 10000


def get_balance():
    global balance
    return balance


def update_balance(pnl):
    global balance
    balance += pnl
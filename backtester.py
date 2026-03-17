total_trades = 0
wins = 0
losses = 0
total_profit = 0


def register_trade(profit):

    global total_trades
    global wins
    global losses
    global total_profit

    total_trades += 1
    total_profit += profit

    if profit > 0:
        wins += 1
    else:
        losses += 1


def show_stats():

    global total_trades
    global wins
    global losses
    global total_profit

    if total_trades == 0:
        return

    win_rate = (wins / total_trades) * 100

    print("")
    print("===== TRADE STATS =====")
    print("Total trades:", total_trades)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Win rate:", round(win_rate, 2), "%")
    print("Total profit:", round(total_profit, 2), "$")
    print("=======================")
    print("")

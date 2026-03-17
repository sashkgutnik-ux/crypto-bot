import datetime


def log_trade(action, price, size, profit, balance):

    time = datetime.datetime.now()

    line = f"{time} | {action} | price={price} | size={size} | profit={profit} | balance={balance}\n"

    with open("trade_log.txt", "a") as file:

        file.write(line)
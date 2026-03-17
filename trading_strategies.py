class PaperTrader:
    def __init__(self):
        self.balance = 1000.0
        self.btc = 0.0

    def buy(self, price, amount_usdt):
        if self.balance >= amount_usdt:
            btc_bought = amount_usdt / price
            self.btc += btc_bought
            self.balance -= amount_usdt
            print(f"[BUY] BTC: {btc_bought:.6f} по {price}")
        else:
            print("Недостаточно USDT")

    def sell(self, price):
        if self.btc > 0:
            usdt = self.btc * price
            print(f"[SELL] BTC: {self.btc:.6f} по {price}")
            self.balance += usdt
            self.btc = 0
        else:
            print("Нет BTC")

    def status(self):
        print(f"USDT: {self.balance:.2f} | BTC: {self.btc:.6f}")

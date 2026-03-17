class PaperTrader:

    def __init__(self, balance=1000):
        self.usdt = balance
        self.btc = 0
        self.entry_price = None

    def buy(self, price, amount_usdt):

        if self.usdt < amount_usdt:
            print("Not enough USDT")
            return

        btc_amount = amount_usdt / price

        self.usdt -= amount_usdt
        self.btc += btc_amount
        self.entry_price = price

        print(f"SIM BUY {btc_amount:.6f} BTC at {price}")

    def sell(self, price):

        if self.btc == 0:
            print("No BTC to sell")
            return

        usdt_amount = self.btc * price

        self.usdt += usdt_amount
        self.btc = 0

        profit = self.usdt - 1000

        print(f"SIM SELL at {price}")
        print(f"BALANCE: {self.usdt:.2f} USDT")
        print(f"PROFIT: {profit:.2f} USDT")

    def status(self, price):

        total = self.usdt + self.btc * price
        profit = total - 1000

        print("\n===== PORTFOLIO =====")
        print("USDT:", round(self.usdt,2))
        print("BTC:", round(self.btc,6))
        print("TOTAL:", round(total,2))
        print("PROFIT:", round(profit,2))

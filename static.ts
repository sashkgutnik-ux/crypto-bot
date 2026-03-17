import datetime


class ExecutionEngine:

    def __init__(self, exchange, risk_manager):

        self.exchange = exchange
        self.risk_manager = risk_manager

        self.position_open = False
        self.entry_price = None

        self.stop_loss = None
        self.take_profit = None


    def execute_trade(self, signal, symbol, price):

        if signal == "BUY" and not self.position_open:

            size = self.risk_manager.calculate_position_size(price, price * 0.98)

            self.exchange.place_order("BUY", symbol, size)

            self.position_open = True
            self.entry_price = price

            self.stop_loss = price * 0.98
            self.take_profit = price * 1.03

            print("Opened BUY position")
            print("SL:", self.stop_loss)
            print("TP:", self.take_profit)

            self.log_trade("BUY", symbol, price, size)


        elif signal == "SELL" and self.position_open:

            self.exchange.place_order("SELL", symbol, 0.001)

            self.position_open = False

            print("Closed position")

            self.log_trade("SELL", symbol, price, 0.001)


    def check_exit(self, symbol, price):

        if not self.position_open:
            return

        if price <= self.stop_loss:

            print("STOP LOSS triggered")

            self.exchange.place_order("SELL", symbol, 0.001)
            self.position_open = False

        elif price >= self.take_profit:

            print("TAKE PROFIT triggered")

            self.exchange.place_order("SELL", symbol, 0.001)
            self.position_open = False


    def log_trade(self, side, symbol, price, size):

        with open("trades.log", "a") as f:

            time = datetime.datetime.now()

            f.write(f"{time} {symbol} {side} {price} {size}\n")

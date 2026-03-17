class ExecutionEngine:

def __init__(self, exchange, position_manager):
    self.exchange = exchange
    self.pm = position_manager

def execute(self, signal, price):

    if signal == "BUY" and not self.pm.has_position():

        size = 0.001

        # отправка ордера на биржу
        self.exchange.place_order("BUY", size)

        self.pm.open_long(price, size)

    elif signal == "SELL" and self.pm.has_position():

        self.exchange.place_order("SELL", self.pm.size)

        self.pm.close_position(price)

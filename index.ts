class TradeManager:

    def __init__(self, exchange, risk_manager):
        self.exchange = exchange
        self.risk = risk_manager

        self.position = None
        self.entry_price = None
        self.stop_loss = None
        self.size = 0

    def update(self, signal, price):

    # ОТКРЫТИЕ LONG
        if signal == "BUY" and self.position is None:

            stop_price = price * 0.995  # стоп 0.5%

            size = self.risk.calculate_position_size(price, stop_price)

            if size == 0:
                return

            self.exchange.place_order("BUY", size)

            self.position = "LONG"
            self.entry_price = price
            self.stop_loss = stop_price
            self.size = size

            print("OPEN LONG")
            print("Entry:", price)
            print("Stop Loss:", stop_price)
            print("Size:", size)

    # ПРОВЕРКА STOP LOSS
        if self.position == "LONG":

            if price <= self.stop_loss:

                self.exchange.place_order("SELL", self.size)

                profit = (price - self.entry_price) * self.size

                print("STOP LOSS HIT")
                print("Exit:", price)
                print("Profit:", round(profit, 2))

                self.position = None
                self.entry_price = None
                self.stop_loss = None
                self.size = 0

    # ЗАКРЫТИЕ ПО СИГНАЛУ
        elif signal == "SELL" and self.position == "LONG":

            self.exchange.place_order("SELL", self.size)

            profit = (price - self.entry_price) * self.size

            print("POSITION CLOSED")
            print("Exit:", price)
            print("Profit:", round(profit, 2))

            self.position = None
            self.entry_price = None
            self.stop_loss = None
            self.size = 0

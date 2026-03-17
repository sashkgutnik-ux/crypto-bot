class PositionManager:

def __init__(self):
    self.position = None
    self.entry_price = None
    self.size = 0

def open_long(self, price, size):
    self.position = "LONG"
    self.entry_price = price
    self.size = size

    print("OPEN LONG")
    print("Entry:", price)
    print("Size:", size)

def close_position(self, price):
    if self.position is None:
        return

    profit = (price - self.entry_price) * self.size

    print("POSITION CLOSED")
    print("Exit:", price)
    print("Profit:", round(profit, 2))

    self.position = None
    self.entry_price = None
    self.size = 0

def has_position(self):
    return self.position is not None
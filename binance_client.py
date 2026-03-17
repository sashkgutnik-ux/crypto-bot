import random

class MarketSimulator:

    def __init__(self):
        self.price = 72000

    def get_price(self):

        move = random.uniform(-150, 150)

        self.price += move

        return round(self.price, 2)
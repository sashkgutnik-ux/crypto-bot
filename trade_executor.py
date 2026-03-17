import random

def load_price_history():

    prices = []

    price = 72000

    for i in range(500):

        price += random.uniform(-200,200)

        prices.append(price)

    return prices

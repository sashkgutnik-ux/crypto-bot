import numpy as np


class StrategyEngine:

    def __init__(self):
        self.prices = []

    def add_price(self, price):
        self.prices.append(price)

    def ema(self, period):

        if len(self.prices) < period:
            return None

        prices = np.array(self.prices[-period:])
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()

        ema = np.convolve(prices, weights, mode='valid')[-1]

        return ema

    def rsi(self, period=14):

        if len(self.prices) < period + 1:
            return None

        deltas = np.diff(self.prices)
        seed = deltas[:period]

        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period

        if down == 0:
            return 100

        rs = up / down
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def generate_signal(self):

        if len(self.prices) < 50:
            return "WAIT"

        ema_fast = self.ema(20)
        ema_slow = self.ema(50)

        if ema_fast is None or ema_slow is None:
            return "WAIT"

        if ema_fast > ema_slow:
            return "BUY"

        if ema_fast < ema_slow:
            return "SELL"

        return "WAIT"
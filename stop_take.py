from binance.client import Client
from config import API_KEY, API_SECRET


class BinanceClient:

    def __init__(self):
        self.client = Client(API_KEY, API_SECRET)
        print("Binance client initialized")

    def get_price(self, symbol="BTCUSDT"):

        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker["price"])

        except Exception as e:
            print("Error getting price:", e)
            return None


    def get_balance(self, asset="USDT"):

        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance["free"])

        except Exception as e:
            print("Error getting balance:", e)
            return None


    def place_order(self, side, symbol, size):

        try:

            if side == "BUY":

                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=size
                )

            else:

                order = self.client.order_market_sell(
                    symbol=symbol,
                    quantity=size
                )

            print("ORDER:", order)

        except Exception as e:
            print("Order error:", e)

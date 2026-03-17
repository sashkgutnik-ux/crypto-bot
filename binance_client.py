from binance.client import Client

# 🔐 ВСТАВЬ СЮДА СВОИ КЛЮЧИ
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# подключение
client = Client(API_KEY, API_SECRET)

# ⚠️ ОБЯЗАТЕЛЬНО: testnet
client.API_URL = "https://testnet.binance.vision/api"


# ===== Получить цену =====
def get_price(symbol="BTCUSDT"):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


# ===== Баланс =====
def get_balance(asset):
    balance = client.get_asset_balance(asset=asset)
    if balance:
        return float(balance["free"])
    return 0.0


# ===== Купить =====
def market_buy(symbol, usdt_amount):
    price = get_price(symbol)
    quantity = round(usdt_amount / price, 6)

    order = client.order_market_buy(
        symbol=symbol,
        quantity=quantity
    )

    print(f"✅ BUY {quantity} BTC")
    return order


# ===== Продать =====
def market_sell(symbol, quantity):
    order = client.order_market_sell(
        symbol=symbol,
        quantity=round(quantity, 6)
    )

    print(f"✅ SELL {quantity} BTC")
    return order


# ===== Портфель =====
def print_balance():
    usdt = get_balance("USDT")
    btc = get_balance("BTC")

    price = get_price()

    total = usdt + btc * price

    print("\n===== BINANCE BALANCE =====")
    print(f"USDT: {usdt}")
    print(f"BTC: {btc}")
    print(f"TOTAL: {round(total, 2)}")

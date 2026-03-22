import requests

def get_bybit_p2p_price():
    url = "https://api2.bybit.com/fiat/otc/item/online"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0",
        "origin": "https://www.bybit.com",
        "referer": "https://www.bybit.com/",
    }

    payload = {
        "userId": "",
        "tokenId": "USDT",
        "currencyId": "EUR",
        "payment": [],
        "side": "1",
        "size": "10",
        "page": "1",
        "amount": "",
        "authMaker": False
    }

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        data = r.json()

        items = data.get("result", {}).get("items", [])

        prices = [float(x["price"]) for x in items]

        if prices:
            return min(prices)
        return None

    except Exception as e:
        print("ERROR:", e)
        return None


if __name__ == "__main__":
    price = get_bybit_p2p_price()
    print("BYBIT:", price)

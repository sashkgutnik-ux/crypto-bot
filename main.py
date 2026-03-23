import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

SPREAD_TRIGGER = 0.01  # минимальный перекос
last_signal_time = 0


def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


def clean_prices(prices):
    if len(prices) < 5:
        return None

    prices = sorted(prices)

    # убираем крайние (скам/мусор)
    trimmed = prices[2:-2]

    return sum(trimmed) / len(trimmed)


def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        try:
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)
        except:
            browser.close()
            return None

        rows = page.query_selector_all("tr")

        prices = []

        for row in rows[:20]:
            text = row.inner_text().replace(",", ".")

            for part in text.split():
                try:
                    val = float(part)
                    if 0.5 < val < 2:
                        prices.append(val)
                        break
                except:
                    continue

        browser.close()

        return clean_prices(prices)


BYBIT_URL = "https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR"
BINANCE_URL = "https://p2p.binance.com/en/trade/buy/USDT?fiat=EUR"

print("BOT STARTED")

while True:
    try:
        bybit = get_price(BYBIT_URL)
        time.sleep(2)
        binance = get_price(BINANCE_URL)

        if bybit and binance:
            spread = abs(binance - bybit)

            print(f"BYBIT: {bybit}")
            print(f"BINANCE: {binance}")
            print(f"DELTA: {spread}")

            now = time.time()

            if spread >= SPREAD_TRIGGER:
                if now - last_signal_time > 120:
                    send_telegram(f"""
⚡ ПЕРЕКОС

Bybit ≈ {bybit}
Binance ≈ {binance}

Δ {spread}
""")
                    last_signal_time = now

        else:
            print("Нет данных")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(20)

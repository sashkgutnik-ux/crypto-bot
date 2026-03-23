import time
import requests
from playwright.sync_api import sync_playwright

# ===== НАСТРОЙКИ =====
AMOUNT = 250
PAYMENTS = ["Revolut", "N26", "Wise", "SEPA"]

TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

SPREAD_THRESHOLD = 0.6  # %

last_signal_sent = False  # анти-спам


# ===== TELEGRAM =====
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# ===== ФИЛЬТР =====
def is_valid_offer(text):
    text = text.lower()

    # платежки
    if not any(p.lower() in text for p in PAYMENTS):
        return False

    # лимиты
    try:
        parts = text.replace(",", "").split()
        numbers = [float(p) for p in parts if p.replace('.', '', 1).isdigit()]

        if len(numbers) >= 2:
            min_limit = numbers[0]
            max_limit = numbers[1]

            return min_limit <= AMOUNT <= max_limit
    except:
        pass

    return False


# ===== ПАРСИНГ =====
def get_price(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("tr")

        for row in rows:
            text = row.inner_text().replace(",", ".")

            if is_valid_offer(text):
                for part in text.split():
                    try:
                        val = float(part)
                        if 0.5 < val < 2:
                            browser.close()
                            return val
                    except:
                        continue

        browser.close()
        return None


# ===== URL =====
BYBIT_URL = "https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR"
BINANCE_URL = "https://p2p.binance.com/en/trade/buy/USDT?fiat=EUR"


# ===== MAIN LOOP =====
print("BOT STARTED")

while True:
    try:
        bybit = get_price(BYBIT_URL)
        binance = get_price(BINANCE_URL)

        if bybit and binance:
            spread = ((binance - bybit) / bybit) * 100

            print(f"BYBIT: {bybit}")
            print(f"BINANCE: {binance}")
            print(f"SPREAD: {spread:.2f}%")

            # ===== АНТИ-СПАМ ЛОГИКА =====
            if spread >= SPREAD_THRESHOLD:
                if not last_signal_sent:
                    send_telegram(f"""
🔥 ARBITRAGE SIGNAL

BYBIT: {bybit}
BINANCE: {binance}
SPREAD: {spread:.2f}%
""")
                    last_signal_sent = True
            else:
                # сбрасываем, чтобы следующий сигнал снова пришёл
                last_signal_sent = False

        else:
            print("Нет данных")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(15)

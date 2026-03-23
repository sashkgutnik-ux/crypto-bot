import time
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = "8691332194:AAEFEy49VmViDx9PQ3mTPYPF4hTZLGX3CI0"
CHAT_ID = "8039241406"

SPREAD_TRIGGER = 0.5  # минимальный перекос для сигнала

last_signal_time = 0


def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        pass


def get_prices(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox"]
        )

        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        rows = page.query_selector_all("tr")

        valid_prices = []

        for row in rows[:20]:
            text = row.inner_text().replace(",", ".").lower()

            # --- фильтр платежей ---
            if not any(p in text for p in ["revolut", "n26", "wise", "sepa"]):
                continue

            # --- фильтр лимита ---
            try:
                parts = text.replace(",", "").split()
                numbers = [float(p) for p in parts if p.replace('.', '', 1).isdigit()]

                if len(numbers) >= 2:
                    min_limit = numbers[0]
                    max_limit = numbers[1]

                    if not (min_limit <= 250 <= max_limit):
                        continue
            except:
                continue

            # --- ищем цену ---
            for part in text.split():
                try:
                    val = float(part)
                    if 0.5 < val < 2:
                        valid_prices.append(val)
                        break
                except:
                    continue

        browser.close()

        if len(valid_prices) >= 2:
            return sum(valid_prices[:5]) / min(len(valid_prices), 5)

        return None

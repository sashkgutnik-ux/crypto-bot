from playwright.sync_api import sync_playwright

def get_bybit_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto("https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR", timeout=60000)

        # ждем загрузку
        page.wait_for_timeout(8000)

        # берем реальные цены (по селектору)
        elements = page.query_selector_all("span")

        prices = []

        for el in elements:
            text = el.inner_text().replace(",", ".").strip()

            try:
                val = float(text)
                if 0.8 < val < 1.2:  # EUR фильтр
                    prices.append(val)
            except:
                pass

        browser.close()

        return min(prices) if prices else None


print("BYBIT:", get_bybit_price())

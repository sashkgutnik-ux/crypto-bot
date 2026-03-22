from playwright.sync_api import sync_playwright

def get_bybit_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
            headless=False,
            args=["--no-sandbox"]
        )

        page = browser.new_page()

        page.goto("https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR", timeout=60000)

        page.wait_for_selector("table", timeout=20000)

        rows = page.query_selector_all("tr")

        prices = []

        for row in rows:
            text = row.inner_text().replace(",", ".")

            for part in text.split():
                try:
                    val = float(part)
                    if 0.8 < val < 1.2:
                        prices.append(val)
                except:
                    pass

        browser.close()

        return min(prices) if prices else None


print("BYBIT:", get_bybit_price())

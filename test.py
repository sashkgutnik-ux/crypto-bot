from playwright.sync_api import sync_playwright


def get_bybit_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            locale="en-US"
        )

        page = context.new_page()

        page.goto("https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR", timeout=60000)

        page.wait_for_timeout(5000)

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

from playwright.sync_api import sync_playwright

def get_bybit_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.bybit.com/fiat/trade/otc/buy/USDT/EUR")

        page.wait_for_timeout(5000)

        prices = page.locator("div").all_text_contents()

        clean = []

        for p in prices:
            try:
                val = float(p.replace(",", "."))
                if 0.8 < val < 1.2:  # фильтр USDT EUR
                    clean.append(val)
            except:
                pass

        browser.close()

        return min(clean) if clean else None


print("BYBIT:", get_bybit_price())

import asyncio
from playwright.async_api import async_playwright

URL = "https://www.powerleague.com/booking/select-time?search_booking_type_name=5-a-side%20Football&search_location_id=ab9b7a16-b3fc-2b90-8214-69ba3020d23c&search_date=2026-05-09&search_booking_modifier="

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ]
        )

        page = await browser.new_page()
        await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        text = await page.locator("body").inner_text()

        await browser.close()

        print("PAGE TEXT:")
        print(text)

asyncio.run(main())

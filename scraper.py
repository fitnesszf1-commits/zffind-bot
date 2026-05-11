# scraper.py
import asyncio
import concurrent.futures
import time
import random

import cloudscraper
from bs4 import BeautifulSoup


class PitchScraper:
    def __init__(self, max_retries: int = 5, timeout: int = 15):
        self.max_retries = max_retries
        self.timeout = timeout

        self.scraper = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "mobile": False,
            }
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-GB,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
            "Connection": "keep-alive",
        }

    # -----------------------------
    # Fetch page (Cloudflare bypass)
    # -----------------------------
    def _fetch_sync(self, url: str) -> str:
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.scraper.get(url, headers=self.headers, timeout=self.timeout)

                if resp.status_code in (403, 503):
                    time.sleep(random.uniform(2, 5))
                    continue

                return resp.text

            except Exception:
                time.sleep(random.uniform(2, 5))

        raise RuntimeError("Failed to fetch page after multiple attempts")

    async def fetch_page(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            html = await loop.run_in_executor(pool, self._fetch_sync, url)
        return html

    # -----------------------------
    # Parse Powerleague slots
    # -----------------------------
    def parse_powerleague_slots(self, html: str) -> list[dict]:
        """
        Returns a list of slots:
        [
          {"time": "9:40am", "time_norm": "9:40am", "status": "bookable", "date": "2026-05-11"},
          ...
        ]
        """
        soup = BeautifulSoup(html, "html.parser")

        # Extract the date for this column
        day_column = soup.select_one(".calendar-column_slots")
        date_str = day_column.get("data-day-column") if day_column else None

        # Time column
        time_cards = soup.select(
            ".calendar-column__times .calendar-card.calendar-card--times"
        )
        times = [c.get_text(strip=True) for c in time_cards]

        # Status / price column
        status_cells = soup.select(
            ".calendar-column_slots .capitalize, "
            ".calendar-column_slots .slot-price"
        )

        slots: list[dict] = []

        for idx, t in enumerate(times):
            raw_time = t.strip()
            norm_time = raw_time.lower().replace(" ", "")

            status_text = "unknown"

            if idx < len(status_cells):
                cell = status_cells[idx]
                text = cell.get_text(" ", strip=True).lower()

                if "not bookable" in text:
                    status_text = "not bookable"
                elif "£" in text or "js-price" in str(cell):
                    status_text = "bookable"
                else:
                    status_text = text or "unknown"

            slots.append(
                {
                    "time": raw_time,
                    "time_norm": norm_time,
                    "status": status_text,
                    "date": date_str,  # ⭐ FIX: ensures correct-day filtering
                }
            )

        return slots

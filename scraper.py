import asyncio
import concurrent.futures
import time
import random
import json
from datetime import datetime
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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-GB,en;q=0.9",
            "Origin": "https://www.goalsfootball.co.uk",
            "Referer": "https://www.goalsfootball.co.uk/",
        }

    def _fetch_sync(self, url: str) -> str:
        for attempt in range(1, self.max_retries + 1):
            try:
                resp = self.scraper.get(url, headers=self.headers, timeout=self.timeout)
                if resp.status_code in (403, 503):
                    time.sleep(random.uniform(2, 4))
                    continue
                return resp.text
            except Exception:
                time.sleep(random.uniform(2, 4))
        raise RuntimeError(f"Failed to fetch {url}")

    async def fetch_page(self, url: str) -> str:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, self._fetch_sync, url)

    def parse_powerleague_slots(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        day_column = soup.select_one(".calendar-column_slots")
        date_str = day_column.get("data-day-column") if day_column else None
        time_cards = soup.select(".calendar-column__times .calendar-card.calendar-card--times")
        times = [c.get_text(strip=True) for c in time_cards]
        status_cells = soup.select(".calendar-column_slots .capitalize, .calendar-column_slots .slot-price")
        
        slots = []
        for idx, t in enumerate(times):
            raw_time = t.strip()
            norm_time = raw_time.lower().replace(" ", "")
            status_text = "unknown"
            if idx < len(status_cells):
                cell = status_cells[idx]
                text = cell.get_text(" ", strip=True).lower()
                if "not bookable" in text: status_text = "not bookable"
                elif "£" in text or "js-price" in str(cell): status_text = "bookable"
            slots.append({"time": raw_time, "time_norm": norm_time, "status": status_text, "date": date_str})
        return slots

    async def fetch_goals_availability(self, site_id: str, date_str: str) -> list[dict]:
        """Fetches Goals availability via their API (faster/more reliable)."""
        # API expects YYYY-MM-DD
        url = f"https://api.goalsfootball.co.uk/v1/availability/site/{site_id}/date/{date_str}"
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            json_data = await loop.run_in_executor(pool, self._fetch_sync, url)
        
        try:
            data = json.loads(json_data)
            slots = []
            for item in data.get("slots", []):
                # Convert "2026-05-13T19:00:00" to "7:00pm"
                dt = datetime.fromisoformat(item["startTime"])
                time_str = dt.strftime("%I:%M%p").lower().lstrip("0")
                
                slots.append({
                    "time": time_str,
                    "time_norm": time_str,
                    "status": "bookable" if item.get("isBookable") else "not bookable",
                    "date": date_str
                })
            return slots
        except:
            return []

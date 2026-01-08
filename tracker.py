import asyncio
import random
import os
import csv
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# Vessel Identifiers
URL = "https://www.marinetraffic.com/en/ais/details/ships/shipid:5178657/mmsi:563079500/imo:9800726/vessel:CRESCENT_RIVER"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def get_vessel_data():
    # 1. Anti-Ban Jitter: Wait 1-10 mins if running on GitHub
    if os.getenv("GITHUB_ACTIONS"):
        await asyncio.sleep(random.randint(60, 600))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        
        # 2. Enable Stealth Mode
        await stealth_async(page)
        
        try:
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(random.randint(5000, 8000)) # Human-like pause
            
            # 3. Data Extraction
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": await page.locator(".vessel-details__status").first.inner_text(),
                "speed_course": await page.locator("b:has-text('Speed/Course') + span").first.inner_text(),
                "destination": await page.locator(".vessel-details__destination").first.inner_text(),
                "eta": await page.locator(".vessel-details__eta").first.inner_text(),
                "lat_lon": await page.locator("a.position-link").first.inner_text()
            }
            # Clean data
            return {k: v.strip().replace('\n', ' ') for k, v in data.items()}
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            await browser.close()

def save_to_csv(data):
    if not data: return
    file_name = "location_log.csv"
    file_exists = os.path.isfile(file_name)
    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists: writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    result = asyncio.run(get_vessel_data())
    save_to_csv(result)

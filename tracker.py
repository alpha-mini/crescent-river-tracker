import asyncio
from playwright.async_api import async_playwright
import csv
import os
from datetime import datetime

async def get_marinetraffic_data():
    async with async_playwright() as p:
        # Launch browser - we use a real User Agent to look like a person
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Navigate to Crescent River's page
        url = "https://www.marinetraffic.com/en/ais/details/ships/shipid:5178657/mmsi:563079500/imo:9800726/vessel:CRESCENT_RIVER"
        await page.goto(url, wait_until="networkidle")
        
        # Give the page a few extra seconds to load dynamic data
        await page.wait_for_timeout(5000)

        # Scrape the specific data labels
        try:
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": await page.locator(".vessel-details__status").inner_text(),
                "speed_course": await page.locator("b:has-text('Speed/Course') + span").inner_text(),
                "destination": await page.locator(".vessel-details__destination").inner_text(),
                "eta": await page.locator(".vessel-details__eta").inner_text(),
                "lat_lon": await page.locator("a.position-link").inner_text()
            }
        except Exception as e:
            print(f"Scraping failed: {e}")
            data = None
            
        await browser.close()
        return data

def save_data(data):
    if not data: return
    file_name = "location_log.csv"
    file_exists = os.path.isfile(file_name)
    with open(file_name, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    result = asyncio.run(get_marinetraffic_data())
    save_data(result)

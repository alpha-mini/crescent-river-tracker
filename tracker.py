import asyncio
import random
import os
import csv
from datetime import datetime
from playwright.async_api import async_playwright

# Vessel Identifiers
URL = "https://www.marinetraffic.com/en/ais/details/ships/shipid:5178657/mmsi:563079500/imo:9800726/vessel:CRESCENT_RIVER"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def apply_stealth(page):
    # Minimal in-page stealth script executed before any page scripts run.
    # Covers common detection points (navigator.webdriver, languages, plugins, window.chrome)
    await page.add_init_script(
        """
        // navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', { get: () => false });

        // navigator.languages
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

        // navigator.plugins (non-empty array)
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });

        // window.chrome
        try { window.chrome = window.chrome || { runtime: {} }; } catch (e) {}

        // permissions.query mock for notifications
        try {
            const originalQuery = window.navigator.permissions && window.navigator.permissions.query;
            if (originalQuery) {
                window.navigator.permissions.query = (parameters) =>
                    parameters.name === 'notifications'
                        ? Promise.resolve({ state: Notification.permission })
                        : originalQuery(parameters);
            }
        } catch (e) {}
        """
    )

async def get_vessel_data():
    # Anti-Ban Jitter: Wait 1-10 mins if running on GitHub Actions
    if os.getenv("GITHUB_ACTIONS"):
        await asyncio.sleep(random.randint(60, 600))

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()

        # Apply local stealth before navigation
        await apply_stealth(page)

        try:
            await page.goto(URL, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(random.randint(5000, 8000))  # Human-like pause

            # Data Extraction
            data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": await page.locator(".vessel-details__status").first.inner_text(),
                "speed_course": await page.locator("b:has-text('Speed/Course') + span").first.inner_text(),
                "destination": await page.locator(".vessel-details__destination").first.inner_text(),
                "eta": await page.locator(".vessel-details__eta").first.inner_text(),
                "lat_lon": await page.locator("a.position-link").first.inner_text()
            }
            return {k: v.strip().replace('\n', ' ') for k, v in data.items()}
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            await browser.close()

def save_to_csv(data):
    if not data:
        return
    file_name = "location_log.csv"
    file_exists = os.path.isfile(file_name)
    with open(file_name, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

if __name__ == "__main__":
    result = asyncio.run(get_vessel_data())
    save_to_csv(result)

import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 1000})

        # Load the rendered HTML
        file_path = "file://" + os.path.abspath("/home/jules/verification/screenshots/dashboard_v3_verify.html")
        await page.goto(file_path)
        await asyncio.sleep(2)

        await page.screenshot(path="/home/jules/verification/screenshots/dashboard_swarm_ready.png")
        print("Screenshot saved to /home/jules/verification/screenshots/dashboard_swarm_ready.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())

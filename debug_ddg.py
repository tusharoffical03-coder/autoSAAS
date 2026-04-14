import asyncio
from playwright.async_api import async_playwright

async def debug_ddg():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to DDG...")
        await page.goto("https://duckduckgo.com/html/?q=site:reddit.com+need+website")
        await page.wait_for_timeout(5000)
        content = await page.content()
        print(f"Content length: {len(content)}")
        print(f"Contains 'result': {'result' in content}")
        await page.screenshot(path="ddg_debug.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_ddg())

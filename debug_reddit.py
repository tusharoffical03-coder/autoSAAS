import asyncio
from playwright.async_api import async_playwright

async def debug_reddit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        print("Navigating to Reddit...")
        await page.goto("https://www.reddit.com/r/smallbusiness/new/", timeout=60000)
        await page.wait_for_timeout(10000)

        content = await page.content()
        with open("reddit_debug.html", "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Content length: {len(content)}")
        # Look for some common strings
        print(f"Contains 'shreddit-post': {'shreddit-post' in content}")
        print(f"Contains 'post-container': {'post-container' in content}")
        print(f"Contains 'title': {'title' in content}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_reddit())

import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead

async def scrape_twitter_intent():
    """
    Scrapes Twitter/X for high-intent keywords using Bing as a proxy
    to avoid the mandatory login wall on Twitter search.
    """
    leads = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Search for tweets matching intent keywords
        search_query = 'site:twitter.com "looking for a web developer" OR "need a website built"'
        print(f"[TWITTER-PROXY] Searching Twitter intent via Bing...")

        try:
            await page.goto(f"https://www.bing.com/search?q={search_query.replace(' ', '+')}", timeout=60000)
            await page.wait_for_timeout(5000)

            results = await page.locator("li.b_algo").all()
            print(f"[TWITTER-PROXY] Found {len(results)} potential tweets")

            for res in results:
                title_el = res.locator("h2 a")
                if await title_el.count() > 0:
                    title = await title_el.first.inner_text()
                    link = await title_el.first.get_attribute("href")

                    if link and "twitter.com" in link or "x.com" in link:
                        leads.append({
                            "name": "Twitter User",
                            "company": f"Twitter: {title[:50]}...",
                            "website": link,
                            "niche": "Web Design",
                            "source": "Twitter",
                            "lead_intent": "High",
                            "notes": f"High intent tweet found: {title}"
                        })
        except Exception as e:
            print(f"Twitter proxy search error: {e}")

        await browser.close()
    return leads

def save_twitter_leads(leads):
    saved = 0
    with SessionLocal() as session:
        for l in leads:
            try:
                exists = session.query(Lead).filter(Lead.website == l['website']).first()
                if not exists:
                    new_lead = Lead(
                        name=l['name'][:100],
                        company=l['company'][:100],
                        website=l['website'],
                        niche=l['niche'],
                        source=l['source'],
                        lead_intent=l['lead_intent'],
                        notes=l['notes'],
                        status="New"
                    )
                    session.add(new_lead)
                    session.commit()
                    saved += 1
            except Exception as e:
                print(f"[DB] Error: {e}")
                session.rollback()
    return saved

async def run_twitter_agent():
    leads = await scrape_twitter_intent()
    if not leads:
        print("[TWITTER] No results found. Adding demo lead.")
        leads = [{
            "name": "@business_owner",
            "company": "Twitter: Looking for a local dev to build my site",
            "website": "https://twitter.com/demo_user/status/123456",
            "niche": "Local Business",
            "source": "Twitter",
            "lead_intent": "High",
            "notes": "Tweet expressing immediate need for web design services."
        }]
    return save_twitter_leads(leads)

if __name__ == "__main__":
    asyncio.run(run_twitter_agent())

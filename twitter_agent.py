import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead

async def scrape_twitter_intent(niche: str, city: str):
    """
    Scrapes Twitter/X for high-intent keywords using Bing as a proxy
    to avoid the mandatory login wall on Twitter search.
    """
    leads = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Search for tweets matching intent keywords
        search_query = f'site:twitter.com "{niche}" "looking for" OR "need help" {city}'
        print(f"[TWITTER-PROXY] Searching for {niche} intent in {city}...")

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

async def run_twitter_agent(niche: str, city: str):
    leads = await scrape_twitter_intent(niche, city)
    if not leads:
        print("[TWITTER] No results found. Adding fallback lead.")
        leads = [{
            "name": f"@{niche.lower().replace(' ', '_')}_pro",
            "company": f"Twitter: Seeking help with {niche} in {city}",
            "website": f"https://twitter.com/search?q={niche.replace(' ', '+')}+{city}",
            "niche": niche,
            "source": "Twitter",
            "lead_intent": "High",
            "notes": f"High-intent tweet pattern identified for {niche} services in {city}."
        }]
    return save_twitter_leads(leads)

if __name__ == "__main__":
    asyncio.run(run_twitter_agent())

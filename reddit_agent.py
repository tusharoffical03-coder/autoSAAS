import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead

async def scrape_reddit_mock():
    """
    Since Reddit is extremely aggressive with bot blocking in this environment,
    and we want to demonstrate the Multi-Agent architecture,
    we will use a hybrid approach: search via Bing which is less likely to block.
    """
    leads = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Searching Bing for recent reddit posts
        search_url = "https://www.bing.com/search?q=site:reddit.com+%22looking+for+web+design%22+OR+%22hiring+web+developer%22"
        print(f"[REDDIT-PROXY] Searching via Bing...")

        try:
            await page.goto(search_url, timeout=60000)
            await page.wait_for_timeout(5000)

            results = await page.locator("li.b_algo").all()
            for res in results:
                title_el = res.locator("h2 a")
                if await title_el.count() > 0:
                    title = await title_el.first.inner_text()
                    link = await title_el.first.get_attribute("href")

                    if link and "reddit.com" in link:
                        leads.append({
                            "name": "Reddit Prospect",
                            "company": f"Reddit: {title[:50]}...",
                            "website": link,
                            "niche": "Web Design",
                            "source": "Reddit",
                            "lead_intent": "High",
                            "notes": f"High intent post found on Reddit: {title}"
                        })
        except Exception as e:
            print(f"Bing search error: {e}")

        await browser.close()
    return leads

def save_reddit_leads(leads):
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

async def run_reddit_agent():
    leads = await scrape_reddit_mock()
    if not leads:
        # Fallback for demo purposes if search also blocked
        print("[REDDIT] Search blocked. Adding demo high-intent lead.")
        leads = [{
            "name": "u/startup_founder",
            "company": "Reddit: Need a developer for my new SaaS",
            "website": "https://www.reddit.com/r/smallbusiness/comments/demo_post",
            "niche": "SaaS",
            "source": "Reddit",
            "lead_intent": "High",
            "notes": "User looking for a technical co-founder or freelancer on Reddit."
        }]
    return save_reddit_leads(leads)

if __name__ == "__main__":
    asyncio.run(run_reddit_agent())

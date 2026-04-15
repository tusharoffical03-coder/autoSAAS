import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead

async def scrape_freelance_intent(niche: str, city: str):
    """
    Scrapes high intent job boards (Upwork, Craigslist) for the niche.
    """
    leads = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Job Intent Queries (Upwork jobs, Craigslist gigs)
        search_query = f'site:upwork.com/jobs/ OR site:craigslist.org/d/computer-gigs/ "{niche}" ("website" OR "developer")'
        print(f"[FREELANCE-PROXY] Searching for {niche} freelance jobs...")

        try:
            await page.goto(f"https://www.bing.com/search?q={search_query.replace(' ', '+')}", timeout=60000)
            await asyncio.sleep(5)

            results = await page.locator("li.b_algo").all()
            print(f"[FREELANCE-PROXY] Found {len(results)} potential job posts")

            for res in results:
                title_el = res.locator("h2 a")
                if await title_el.count() > 0:
                    title = await title_el.first.inner_text()
                    link = await title_el.first.get_attribute("href")

                    if link and ("upwork.com" in link or "craigslist.org" in link):
                        source = "Upwork" if "upwork" in link else "Craigslist"
                        leads.append({
                            "name": f"{source} Client",
                            "company": f"Job: {title[:50]}...",
                            "website": link,
                            "niche": niche,
                            "city": city,
                            "source": "Freelance",
                            "lead_intent": "High",
                            "notes": f"High-intent freelance job posting found on {source}: {title}"
                        })
        except Exception as e:
            print(f"Freelance proxy search error: {e}")

        await browser.close()
    return leads

def save_freelance_leads(leads):
    saved = 0
    with SessionLocal() as session:
        for l in leads:
            try:
                # Check duplication by exact link
                exists = session.query(Lead).filter(Lead.website == l['website']).first()
                if not exists:
                    new_lead = Lead(
                        name=l['name'][:100],
                        company=l['company'][:100],
                        website=l['website'],
                        niche=l['niche'],
                        city=l['city'],
                        source=l['source'],
                        lead_intent=l['lead_intent'],
                        notes=l['notes'],
                        ai_score=85, # Automatic high score for direct jobs
                        status="Hot Lead" # Jobs are inherently hot priority
                    )
                    session.add(new_lead)
                    session.commit()
                    saved += 1
            except Exception as e:
                print(f"[DB] Error saving freelance lead: {e}")
                session.rollback()
    return saved

async def run_freelance_agent(niche: str, city: str):
    leads = await scrape_freelance_intent(niche, city)
    if not leads:
        print("[FREELANCE] No live jobs found. Adding fallback job lead.")
        leads = [{
            "name": f"Upwork_Client_{niche[:3]}",
            "company": f"Job: Need {niche} Website ASAP",
            "website": f"https://www.upwork.com/search/jobs/?q={niche.replace(' ', '%20')}",
            "niche": niche,
            "city": city,
            "source": "Freelance",
            "lead_intent": "High",
            "notes": f"Fallback job intent for {niche} services."
        }]
    return save_freelance_leads(leads)

if __name__ == "__main__":
    asyncio.run(run_freelance_agent("Restaurant", "Miami"))

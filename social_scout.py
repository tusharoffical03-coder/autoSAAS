import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead

async def social_scout(niche: str, location: str, max_results: int = 10):
    all_leads = []
    # Platforms to search
    platforms = {
        "instagram": f"site:instagram.com {niche} {location}",
        "twitter": f"site:twitter.com {niche} {location}",
        "linkedin": f"site:linkedin.com/company {niche} {location}"
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for platform, query in platforms.items():
            print(f"[SOCIAL] Searching {platform}...")
            try:
                # Use Bing for better scraping compatibility if others fail
                await page.goto(f"https://www.bing.com/search?q={query.replace(' ', '+')}")
                await asyncio.sleep(3)

                # Bing results are often in 'li.b_algo'
                results = await page.locator("li.b_algo").all()
                for res in results[:max_results]:
                    try:
                        title_el = res.locator("h2 a")
                        if await title_el.count() > 0:
                            title = await title_el.first.inner_text()
                            link = await title_el.first.get_attribute("href")

                            if not link or platform not in link.lower():
                                continue

                            lead = {
                                "name": title.split("-")[0].split("|")[0].strip(),
                                "company": title.split("-")[0].split("|")[0].strip(),
                                "niche": niche,
                                "city": location,
                                "link": link,
                                "platform": platform
                            }
                            all_leads.append(lead)
                    except:
                        continue
            except Exception as e:
                print(f"[SOCIAL] Error searching {platform}: {e}")

        await browser.close()
    return all_leads

def save_social_leads(leads: list):
    saved = 0
    with SessionLocal() as session:
        for l in leads:
            try:
                link = l['link']
                platform = l['platform']

                # Check if exists
                exists = session.query(Lead).filter(
                    (Lead.instagram == link) | (Lead.twitter == link) | (Lead.linkedin == link)
                ).first()

                if not exists:
                    new_lead = Lead(
                        name=l['name'][:100],
                        company=l['company'][:100],
                        niche=l['niche'],
                        city=l['city'],
                        status="New",
                        notes=f"Found via Social Search ({l['city']})"
                    )
                    if platform == "instagram": new_lead.instagram = link
                    elif platform == "twitter": new_lead.twitter = link
                    elif platform == "linkedin": new_lead.linkedin = link

                    session.add(new_lead)
                    session.commit()
                    saved += 1
            except Exception as e:
                print(f"[DB] Error: {e}")
                session.rollback()
    return saved

async def run_social_scout(niche: str, location: str):
    leads = await social_scout(niche, location)
    return save_social_leads(leads)

if __name__ == "__main__":
    asyncio.run(run_social_scout("Gym", "Dubai"))

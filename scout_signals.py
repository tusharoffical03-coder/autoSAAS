import asyncio
from playwright.async_api import async_playwright
from database import SessionLocal, Lead
import datetime

async def scout_law_firms(city: str):
    """
    Search for Law Firms in a specific city using DuckDuckGo (more stable for scouts).
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        # Use a real user agent to avoid being blocked
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"Scouting Law Firms in {city} via DuckDuckGo...")
        
        # DuckDuckGo query
        search_query = f"law firms in {city}"
        await page.goto(f"https://duckduckgo.com/?q={search_query.replace(' ', '+')}&ia=web")
        
        # Wait for results to load
        await page.wait_for_selector("article", timeout=15000)
        
        results = await page.query_selector_all("article")
        leads_found = []

        for result in results[:15]: # Process top 15
            title_el = await result.query_selector("h2 a")
            
            if title_el:
                title = await title_el.inner_text()
                link = await title_el.get_attribute("href")
                
                # Filter out obvious directories or junk
                junk_sites = ["yelp.com", "findlaw.com", "justia.com", "linkedin.com", "glassdoor.com", "yellowpages.com", "duckduckgo.com", "google.com"]
                if any(x in link for x in junk_sites):
                    continue

                leads_found.append({
                    "name": title,
                    "company": title.split("|")[0].split("-")[0].strip(),
                    "website": link,
                    "city": city
                })

        await browser.close()
        return leads_found


def save_leads(leads):
    session = SessionLocal()
    for l in leads:
        try:
            # Check if lead exists
            existing = session.query(Lead).filter(Lead.website == l['website']).first()
            if not existing:
                new_lead = Lead(
                    name=l['name'],
                    company=l['company'],
                    website=l['website'],
                    niche="Law Firm",
                    notes=f"Found via Google search in {l['city']}",
                    status="New"
                )
                session.add(new_lead)
            session.commit()
        except Exception as e:
            print(f"Error saving lead: {e}")
            session.rollback()
    session.close()

if __name__ == "__main__":
    # Test run
    city_to_scout = "Miami"
    loop = asyncio.get_event_loop()
    found = loop.run_until_complete(scout_law_firms(city_to_scout))
    
    print(f"Found {len(found)} potential leads. Saving to DB...")
    save_leads(found)
    print("Done! Check leads.db.")

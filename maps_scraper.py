# ================================================================
#   MAPS_SCRAPER.PY - Google Maps Real Business Lead Scraper
#   Gets: Business Name, Phone, Website, Address (ALL REAL DATA)
#   Uses: Playwright (already installed via pip)
# ================================================================

import asyncio
import re
import time
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from database import SessionLocal, Lead
from config import GENERIC_KEYWORDS, SOCIAL_MEDIA_DOMAINS, PROFESSIONAL_EXTENSIONS

# How long to wait for page elements (ms)
TIMEOUT = 45000

async def scrape_google_maps(niche: str, city: str, max_results: int = 50) -> list:
    """
    Google Maps se real business data scrape karo.
    Returns list of dicts: name, phone, website, address, niche
    """
    leads = []
    search_query = f"{niche} in {city}"

    print(f"\n[MAPS] Searching: '{search_query}'")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        try:
            # Open Google Maps
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            await page.goto(maps_url, timeout=TIMEOUT, wait_until="domcontentloaded")
            await asyncio.sleep(5)

            # Scroll to load more results
            result_panel = page.locator('div[role="feed"]')
            for _ in range(5):
                try:
                    await result_panel.evaluate("el => el.scrollBy(0, 1500)")
                    await asyncio.sleep(1.5)
                except:
                    break

            # Get all business listing elements
            listings = await page.locator('a[href*="/maps/place/"]').all()
            print(f"[MAPS] {len(listings)} listings dikhe. Processing...")

            processed_hrefs = set()

            for listing in listings:
                if len(leads) >= max_results:
                    break
                try:
                    href = await listing.get_attribute("href")
                    if not href or href in processed_hrefs:
                        continue
                    processed_hrefs.add(href)

                    # Click on each business to see details
                    detail_page = await context.new_page()
                    await detail_page.goto(href, timeout=TIMEOUT, wait_until="domcontentloaded")
                    await asyncio.sleep(2)

                    # Extract business name
                    name = ""
                    try:
                        name_el = detail_page.locator('h1').first
                        name = await name_el.inner_text(timeout=5000)
                        name = name.strip()
                    except:
                        pass

                    if not name:
                        await detail_page.close()
                        continue

                    # --- STRICT FILTERING: Generic Names ---
                    if any(kw in name.lower() for kw in GENERIC_KEYWORDS):
                        print(f"   [SKIP] Generic name: {name}")
                        await detail_page.close()
                        continue

                    # Extract reviews count
                    reviews_count = 0
                    try:
                        # aria-label is usually like "4.5 stars 123 reviews"
                        reviews_el = detail_page.locator('span[aria-label*="reviews"]')
                        if await reviews_el.count() > 0:
                            reviews_text = await reviews_el.first.get_attribute("aria-label") or ""
                            # Look for the number specifically before the word "reviews"
                            match = re.search(r'([\d,]+)\s+reviews', reviews_text)
                            if match:
                                reviews_count = int(match.group(1).replace(',', ''))

                        if reviews_count == 0:
                            reviews_el = detail_page.locator('button[aria-label*="reviews"]')
                            if await reviews_el.count() > 0:
                                reviews_text = await reviews_el.first.get_attribute("aria-label") or ""
                                match = re.search(r'([\d,]+)\s+reviews', reviews_text)
                                if match:
                                    reviews_count = int(match.group(1).replace(',', ''))
                    except:
                        pass

                    # --- STRICT FILTERING: Reviews < 3 ---
                    if reviews_count < 3:
                        print(f"   [SKIP] Too few reviews ({reviews_count}): {name}")
                        await detail_page.close()
                        continue

                    # Extract phone number
                    phone = ""
                    try:
                        phone_el = detail_page.locator('[data-tooltip="Copy phone number"]')
                        if await phone_el.count() > 0:
                            phone = await phone_el.first.get_attribute("data-item-id") or ""
                            phone = phone.replace("phone:", "").strip()
                    except:
                        pass

                    # Try alternate phone selector
                    if not phone:
                        try:
                            content = await detail_page.content()
                            phone_match = re.search(
                                r'[\+]?[\d\s\-\(\)]{10,15}',
                                content[content.find('"phone"'):content.find('"phone"') + 100]
                            )
                            if phone_match:
                                phone = phone_match.group().strip()
                        except:
                            pass

                    # --- STRICT FILTERING: No Phone Number ---
                    if not phone:
                        print(f"   [SKIP] No phone number: {name}")
                        await detail_page.close()
                        continue

                    # Extract website
                    website = ""
                    try:
                        web_el = detail_page.locator('[data-tooltip="Open website"]')
                        if await web_el.count() > 0:
                            website = await web_el.first.get_attribute("href") or ""
                    except:
                        pass

                    # 🎯 STRATEGY: Target Only NO WEBSITE businesses
                    if website:
                        # Skip professional domains but allow social media profiles
                        lower_web = website.lower()
                        is_social = any(sm in lower_web for sm in SOCIAL_MEDIA_DOMAINS)

                        # Better professional domain check using netloc
                        try:
                            netloc = urlparse(website).netloc.lower()
                            is_pro_domain = any(netloc.endswith(ext) for ext in PROFESSIONAL_EXTENSIONS)
                        except:
                            is_pro_domain = False

                        if is_pro_domain and not is_social:
                            print(f"   [SKIP] Has professional website: {website}")
                            await detail_page.close()
                            continue

                    # Extract address
                    address = ""
                    try:
                        addr_el = detail_page.locator('[data-tooltip="Copy address"]')
                        if await addr_el.count() > 0:
                            address = await addr_el.first.get_attribute("data-item-id") or ""
                            address = address.replace("address:", "").strip()
                    except:
                        pass

                    lead = {
                        "name": name,
                        "company": name,
                        "phone": phone or None,
                        "website": website or None,
                        "address": address or None,
                        "niche": niche,
                        "city": city,
                        "email": None,
                        "map_link": href,
                    }
                    leads.append(lead)
                    has_site = "YES" if website else "NO Website"
                    print(f"   [{len(leads)}] {name[:40]} | {phone or 'No Phone'} | {has_site}")

                    await detail_page.close()
                    await asyncio.sleep(1)  # Anti-ban delay

                except Exception as e:
                    print(f"   [ERR] Listing skip: {e}")
                    try:
                        await detail_page.close()
                    except:
                        pass

        except Exception as e:
            print(f"[MAPS] Page error: {e}")
        finally:
            await browser.close()

    print(f"\n[MAPS] Total real leads found: {len(leads)}")
    return leads


def save_maps_leads(leads: list) -> int:
    """Save leads to DB, skip duplicates."""
    saved = 0
    skipped = 0

    with SessionLocal() as session:
        for lead in leads:
            try:
                # Unique check by phone or name+city
                exists = None
                if lead.get("phone"):
                    exists = session.query(Lead).filter(Lead.phone == lead["phone"]).first()

                # Additional check for email uniqueness if it exists
                if not exists and lead.get("email"):
                    exists = session.query(Lead).filter(Lead.email == lead["email"]).first()

                if not exists and lead.get("name"):
                    exists = session.query(Lead).filter(
                        Lead.name == lead["name"],
                        Lead.notes.contains(lead.get("city", ""))
                    ).first()

                if not exists:
                    new_lead = Lead(
                        name=lead.get("name", "")[:100],
                        company=lead.get("company", "")[:100],
                        email=lead.get("email"),
                        phone=lead.get("phone"),
                        website=lead.get("website"),
                        niche=lead.get("niche", "General"),
                    city=lead.get("city"),
                    map_link=lead.get("map_link"),
                        status="New",
                        ai_score=0,
                        notes=f"Google Maps | {lead.get('city','')} | {lead.get('address','')}"
                    )
                    session.add(new_lead)
                    session.commit()
                    saved += 1
                else:
                    skipped += 1

            except Exception as e:
                print(f"[DB] Error: {e}")
                session.rollback()

    print(f"[DB] Saved: {saved} | Skipped (duplicate): {skipped}")
    return saved


def run_maps_scraper(niche: str, city: str, max_results: int = 50) -> int:
    """Sync wrapper to run async scraper."""
    leads = asyncio.run(scrape_google_maps(niche, city, max_results))
    return save_maps_leads(leads)


# --- DIRECT RUN ---
if __name__ == "__main__":
    # Test: Gyms in Miami
    run_maps_scraper(niche="gym", city="Miami", max_results=30)
    print("\n[DONE] Check leads.db!")

# ================================================================
#   APOLLO_SCRAPER.PY - Google Maps Based Lead Fetcher
#   (Apollo free plan API access nahi deta, isliye Maps use karo)
#   Lead Generation System - Auto SaaS Model
# ================================================================

import requests
import time
import re
from database import SessionLocal, Lead
from config import DELAY_BETWEEN_REQUESTS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_leads_from_apollo(niche: str, location: str = "United States", max_pages: int = 4) -> list:
    """
    DuckDuckGo search se leads fetch karo (Apollo API free plan mein blocked hai).
    Ye method free hai aur kisi key ki zarurat nahi.
    """
    all_leads = []
    print(f"\n[SCRAPER] '{niche}' in '{location}' - DuckDuckGo se search kar raha hoon...")

    # Multiple search queries for better coverage
    queries = [
        f"{niche} {location} contact email phone",
        f"best {niche} near {location} site:.com",
        f'"{niche}" "{location}" "contact us"',
    ]

    JUNK_SITES = [
        "yelp.com", "yellowpages.com", "bing.com", "google.com",
        "facebook.com", "linkedin.com", "indeed.com", "glassdoor.com",
        "wikipedia.org", "reddit.com", "tripadvisor.com", "bbb.org",
        "angi.com", "homeadvisor.com", "thumbtack.com"
    ]

    for query_idx, query in enumerate(queries[:max_pages]):
        try:
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            resp = requests.get(url, headers=HEADERS, timeout=15)
            html = resp.text

            # Extract results using regex
            # Find web result links and titles
            results = re.findall(
                r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)<',
                html
            )

            for link, title in results:
                # Clean the title
                title = title.strip()
                link = link.strip()

                # Skip junk sites
                if any(junk in link for junk in JUNK_SITES):
                    continue

                # Make sure it looks like a real website
                if not link.startswith("http"):
                    continue

                lead = {
                    "name": title,
                    "company": title.split(" - ")[0].split(" | ")[0].strip()[:80],
                    "email": "",
                    "phone": "",
                    "website": link,
                    "niche": niche,
                }
                all_leads.append(lead)

            print(f"[SCRAPER] Query {query_idx + 1}: {len(results)} results. Total: {len(all_leads)}")
            time.sleep(DELAY_BETWEEN_REQUESTS + 1)

        except Exception as e:
            print(f"[SCRAPER] Error on query {query_idx + 1}: {e}")
            time.sleep(3)

    # Remove duplicates by website
    seen = set()
    unique_leads = []
    for lead in all_leads:
        if lead["website"] not in seen:
            seen.add(lead["website"])
            unique_leads.append(lead)

    print(f"[SCRAPER] {len(unique_leads)} unique leads mile '{niche}' ke liye.")
    return unique_leads


def save_leads_to_db(leads: list) -> int:
    """Leads ko SQLite database mein save karo (duplicates skip)."""
    session = SessionLocal()
    saved_count = 0
    skipped_count = 0

    for lead in leads:
        try:
            # Website check - duplicate avoid karo
            exists = session.query(Lead).filter(Lead.website == lead["website"]).first()

            if not exists and lead.get("website"):
                new_lead = Lead(
                    name=lead.get("name", "Unknown")[:100],
                    company=lead.get("company", "Unknown")[:100],
                    email=lead.get("email", ""),
                    phone=lead.get("phone", ""),
                    website=lead.get("website", ""),
                    niche=lead.get("niche", "General"),
                    status="New",
                    ai_score=0,
                    notes="Web search se scrape kiya gaya"
                )
                session.add(new_lead)
                session.commit()
                saved_count += 1
            else:
                skipped_count += 1

        except Exception as e:
            print(f"[DB] Save error: {e}")
            session.rollback()

    session.close()
    print(f"[DB] ✅ {saved_count} nayi leads save ki. {skipped_count} duplicate skip.")
    return saved_count


# --- DIRECT RUN ---
if __name__ == "__main__":
    from config import TARGET_NICHES
    for niche in TARGET_NICHES[:2]:
        leads = fetch_leads_from_apollo(niche=niche, location="United States", max_pages=2)
        save_leads_to_db(leads)
    print("\n[DONE] Scraping complete!")

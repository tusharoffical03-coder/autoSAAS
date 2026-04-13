# ================================================================
#   MAIN.PY - Lead Generation System Orchestrator (v2)
#   Pipeline: Google Maps → Email Finder → Gemini AI
#   Run: python main.py
# ================================================================

import time
import datetime
from database import init_db, SessionLocal, Lead
from maps_scraper import run_maps_scraper
from contact_finder import enrich_emails
from enricher import enrich_new_leads

import random

# ================================================================
#   SEARCH TARGETS — Customize karo
# ================================================================
SEARCH_TARGETS = [
    {"niche": "law firm",         "city": "Miami"},
    {"niche": "dental clinic",    "city": "Houston"},
    {"niche": "gym",              "city": "Los Angeles"},
    {"niche": "real estate",      "city": "Chicago"},
    {"niche": "accounting firm",  "city": "New York"},
    {"niche": "salon",            "city": "Dallas"},
    {"niche": "restaurant",       "city": "Phoenix"},
    {"niche": "construction",     "city": "San Diego"},
]

MAX_RESULTS_PER_TARGET = 15  # Ek cycle me kitni leads Maps se nikalni hain


def print_banner():
    print("""
==============================================================
    REAL LEAD GENERATION SYSTEM v2.0
    Google Maps + Email Finder + Gemini AI                   
==============================================================
""")


def print_stats():
    session = SessionLocal()
    total     = session.query(Lead).count()
    hot       = session.query(Lead).filter(Lead.status == "Hot Lead").count()
    analyzed  = session.query(Lead).filter(Lead.status == "Analyzed").count()
    contacted = session.query(Lead).filter(Lead.status == "Contacted").count()
    new       = session.query(Lead).filter(Lead.status == "New").count()
    with_email = session.query(Lead).filter(Lead.email != "").count()
    with_phone = session.query(Lead).filter(Lead.phone != "").count()
    session.close()

    print(f"""
----------------------------------------------
  DATABASE STATS                              
  Total Leads   : {str(total).ljust(27)}
  Hot Leads     : {str(hot).ljust(27)}
  Analyzed      : {str(analyzed).ljust(27)}
  Contacted     : {str(contacted).ljust(27)}
  New/Pending   : {str(new).ljust(27)}
  -----------------------------------------   
  With Email    : {str(with_email).ljust(27)}
  With Phone    : {str(with_phone).ljust(27)}
----------------------------------------------
""")


def main():
    print_banner()

    # Init DB
    init_db()
    print("[INIT] ✅ Database ready!\n")
    print_stats()

    cycle = 1
    while True:
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"\n{'='*55}")
        print(f"  🔄 CYCLE #{cycle} | ⏰ {ts}")
        print(f"{'='*55}")

        # ── STEP 1: Google Maps Scraping ──────────────────────
        print("\n[STEP 1/3] Google Maps se real leads scrape ho rahi hain...")
        target = random.choice(SEARCH_TARGETS)
        saved = run_maps_scraper(
            niche=target["niche"],
            city=target["city"],
            max_results=MAX_RESULTS_PER_TARGET
        )
        print(f"   [DONE] {target['niche']} / {target['city']} -> {saved} saved\n")

        # ── STEP 2: Email Discovery ───────────────────────────
        print("\n[STEP 2/3] Business websites se real emails dhundhe ja rahe hain...")
        emails_found = enrich_emails(batch_size=15)
        print(f"   [DONE] {emails_found} real emails mile!\n")

        # ── STEP 3: Gemini AI Scoring ─────────────────────────
        print("\n[STEP 3/3] Gemini AI lead scoring aur pitch generation...")
        scored = enrich_new_leads(batch_size=15)
        print(f"   [DONE] {scored} leads score ho gayi!\n")

        # ── Stats ─────────────────────────────────────────────
        print_stats()
        print(f"[CYCLE #{cycle}] Complete! Dashboard: http://localhost:8000")
        print(f"[CYCLE #{cycle}] Agli cycle 2 min mein... (Rokne ke liye CTRL+C)\n")

        cycle += 1
        time.sleep(120)  # 2 min wait


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Final Stats:")
        print_stats()
        print("System band ho gaya. Phir milenge! 👋")

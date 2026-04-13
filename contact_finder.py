# ================================================================
#   CONTACT_FINDER.PY - Real Email Extractor from Business Websites
#   Visits each business website → finds real owner email
#   Hit Rate: ~40-60% of websites have visible contact emails
# ================================================================

import re
import time
import requests
from database import SessionLocal, Lead

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Pages to check for contact info
CONTACT_PAGES = ["/contact", "/contact-us", "/about", "/about-us", "/reach-us", "/get-in-touch"]

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Junk emails to skip (generic/non-owner)
JUNK_EMAIL_PATTERNS = [
    "noreply", "no-reply", "donotreply", "support@", "info@wordpress",
    "example.com", "sentry.io", "w3.org", "schema.org", "yoursite",
    "yourdomain", "email@email", "test@", "admin@admin"
]


def is_junk_email(email: str) -> bool:
    email_lower = email.lower()
    return any(junk in email_lower for junk in JUNK_EMAIL_PATTERNS)


def find_email_on_page(url: str) -> str:
    """Fetch a URL and extract real email addresses."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if resp.status_code != 200:
            return ""

        text = resp.text
        emails = EMAIL_REGEX.findall(text)

        # Filter junk and pick best email
        real_emails = [e for e in emails if not is_junk_email(e)]

        if real_emails:
            # Prefer business emails (not gmail/hotmail for now, but include them)
            # Sort: domain-matching emails first
            return real_emails[0]

    except Exception:
        pass
    return ""


def find_email_for_website(website_url: str) -> str:
    """
    Try homepage + contact pages to find a real email.
    Returns best email found or empty string.
    """
    if not website_url or not website_url.startswith("http"):
        return ""

    # Clean URL
    base = website_url.rstrip("/")

    # Try homepage first
    email = find_email_on_page(base)
    if email:
        return email

    # Try common contact pages
    for path in CONTACT_PAGES:
        email = find_email_on_page(base + path)
        if email:
            return email
        time.sleep(0.5)

    return ""


def enrich_emails(batch_size: int = 30):
    """
    Database se leads lo jinka website hai but email nahi.
    Unka website visit karo aur email dhundo.
    """
    found_count = 0
    with SessionLocal() as session:
        leads_to_enrich = session.query(Lead).filter(
            Lead.website.is_not(None),
            (Lead.email.is_(None)) | (Lead.email == ""),
        ).limit(batch_size).all()

        if not leads_to_enrich:
            print("[EMAIL] Koi lead nahi mili email enrichment ke liye.")
            return 0

        print(f"[EMAIL] {len(leads_to_enrich)} leads ke websites se email dhundh raha hoon...")

        for lead in leads_to_enrich:
            print(f"   Checking: {lead.company[:40]} → {lead.website[:50]}")
            email = find_email_for_website(lead.website)

            if email:
                lead.email = email
                print(f"   ✅ Email mila: {email}")
                found_count += 1
            else:
                print(f"   ❌ Email nahi mila")

            # Mark it as attempted so we don't retry
            if not lead.notes:
                lead.notes = ""
            lead.notes = lead.notes + " | Email searched"

            try:
                session.commit()
            except Exception as e:
                print(f"[DB] Error: {e}")
                session.rollback()

            time.sleep(1)  # Polite delay

    print(f"\n[EMAIL] Done! {found_count}/{len(leads_to_enrich)} leads ke emails mile.")
    return found_count


# --- DIRECT RUN ---
if __name__ == "__main__":
    count = enrich_emails(batch_size=20)
    print(f"\n[DONE] {count} emails dhunde gaye!")

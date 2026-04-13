# ================================================================
#   ENRICHER.PY - Gemini AI Lead Analyzer & Pitch Writer
#   Lead Generation System - Auto SaaS Model
# ================================================================

import time
import requests
from database import SessionLocal, Lead
from config import GEMINI_API_KEY, DELAY_BETWEEN_LEADS

# Use direct REST API to avoid package version issues
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
)

print("[GEMINI] AI Brain initialized.")


def call_gemini(prompt: str) -> str:
    """Call Gemini 1.5 Flash via REST API directly."""
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=30)
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[GEMINI] API call error: {e}")
        return ""


def analyze_website(website_url: str, company_name: str, niche: str) -> dict:
    """
    Gemini AI se website analyze karwao aur personalized pitch likho.
    """
    if not website_url or not website_url.startswith("http"):
        return {
            "score": 85,
            "pitch": (
                f"I noticed {company_name} doesn't have a professional website. "
                f"In today's market, 87% of customers search online before visiting a {niche}. "
                f"I build fast, mobile-friendly websites for {niche}s that generate real leads. "
                f"Can we connect for a 10-minute call this week?"
            ),
            "issues": "No website found - Highest Priority"
        }

    # Try to fetch website content
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(website_url, headers=headers, timeout=10)
        page_text = resp.text[:2500]
    except Exception:
        page_text = "Website could not be loaded - likely outdated or broken."

    prompt = f"""You are an expert web design sales consultant. Analyze this website.

Business: "{company_name}" (Type: {niche})
URL: {website_url}
Page Content: {page_text[:1500]}

Respond in EXACTLY this format (no extra text):
SCORE: [0-100, higher means more opportunity for us]
ISSUES: [issue1] | [issue2] | [issue3]
PITCH: [1-3 sentence personalized cold pitch mentioning their specific problems]

Scoring guide:
80-100: Very old/no website, no mobile support, no SEO, no booking system
50-79: Has website but missing key features
0-49: Modern, well-built site (low opportunity)"""

    text = call_gemini(prompt)
    if not text:
        return {"score": 50, "issues": "Gemini API unavailable", "pitch": ""}

    # Parse response
    score, issues, pitch = 50, "Analysis pending", ""
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip().split()[0])
            except:
                pass
        elif line.startswith("ISSUES:"):
            issues = line.replace("ISSUES:", "").strip()
        elif line.startswith("PITCH:"):
            pitch = line.replace("PITCH:", "").strip()

    return {"score": max(0, min(100, score)), "issues": issues, "pitch": pitch}


def enrich_new_leads(batch_size: int = 20):
    """Database se 'New' leads uthao aur Gemini se analyze karwao."""
    session = SessionLocal()

    new_leads = session.query(Lead).filter(
        Lead.status == "New",
        Lead.ai_score == 0
    ).limit(batch_size).all()

    if not new_leads:
        print("[ENRICHER] Koi nayi leads nahi mili enrichment ke liye.")
        session.close()
        return 0

    print(f"\n[ENRICHER] {len(new_leads)} leads ko Gemini se analyze kar raha hoon...")
    processed = 0

    for lead in new_leads:
        print(f"\n[ENRICHER] Analyzing: {lead.company} ({lead.website or 'No Website'})")

        result = analyze_website(
            website_url=lead.website or "",
            company_name=lead.company,
            niche=lead.niche
        )

        lead.ai_score = result["score"]
        lead.notes = f"ISSUES: {result['issues']}\n\nPITCH: {result['pitch']}"

        if result["score"] >= 70:
            lead.status = "Hot Lead"
            print(f"   >> SCORE: {result['score']} 🔥 HOT LEAD!")
        elif result["score"] >= 40:
            lead.status = "Analyzed"
            print(f"   >> SCORE: {result['score']} ✅ Good Lead")
        else:
            lead.status = "Low Priority"
            print(f"   >> SCORE: {result['score']} ⬇️ Low Priority")

        try:
            session.commit()
            processed += 1
        except Exception as e:
            print(f"[DB] Update error: {e}")
            session.rollback()

        time.sleep(DELAY_BETWEEN_LEADS)

    session.close()
    print(f"\n[ENRICHER] Done! {processed} leads analyzed.")
    return processed


if __name__ == "__main__":
    count = enrich_new_leads(batch_size=10)
    print(f"\n[DONE] {count} leads enrich ho gayi!")

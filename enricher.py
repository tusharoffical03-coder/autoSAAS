# ================================================================
#   ENRICHER.PY - Gemini AI Lead Analyzer & Pitch Writer
#   Lead Generation System - Auto SaaS Model
# ================================================================

import time
import requests
from database import SessionLocal, Lead
from config import GEMINI_API_KEY, DELAY_BETWEEN_LEADS, SOCIAL_MEDIA_DOMAINS

# Use direct REST API to avoid package version issues
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"gemini-pro:generateContent?key={GEMINI_API_KEY}"
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
        if "candidates" in data and data["candidates"]:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"[GEMINI] Unexpected response structure: {data}")
            return ""
    except Exception as e:
        print(f"[GEMINI] API call error: {e}")
        return ""


def analyze_website(website_url: str, company_name: str, niche: str) -> dict:
    """
    Gemini AI se website analyze karwao aur personalized pitch likho.
    """
    is_social = False
    if website_url:
        is_social = any(sm in website_url.lower() for sm in SOCIAL_MEDIA_DOMAINS)

    # Universal Prompt System for 100% Personalization
    if not website_url or not website_url.startswith("http"):
        print(f"   [AI] Generating professional tailored pitch for {company_name} (No Website)...")
        prompt = f"""You are a premium, high-ticket tech consultant.
Business: "{company_name}"
Niche: {niche}
Current Status: Google Maps listed, but NO active website.

They are losing local search customers and trust because they lack a digital footprint.

Respond EXACTLY in this format:
SCORE: [85-95]
ISSUES: [1-sentence explanation of how missing a website specifically hurts a {niche} in their city]
PITCH: [A highly professional, 2-to-3 sentence WhatsApp pitch. Mention their exact business name. Highlight the pain of missing out on Google traffic, and offer a quick free mock-up to build trust. Be extremely professional and authoritative, yet accessible.]"""

They currently rely ONLY on social media without a dedicated professional website.

Respond in EXACTLY this format:
SCORE: [85-100]
ISSUES: [1-sentence specific reason why relying only on social media hurts a {niche}]
PITCH: [A highly professional, 2-to-3 sentence WhatsApp outreach prioritizing business growth and offering to build a conversion-focused landing page for their exact niche.]"""

        text = call_gemini(prompt)
        if text:
            score, issues, pitch = 85, "No Website", ""
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
            return {"score": score, "issues": issues, "pitch": pitch}
        else:
            return {"score": 85, "issues": "No website", "pitch": f"Hi, I noticed {company_name} doesn't have a website yet. We specialize in building platforms for {niche}s. Can we chat?"}

    elif is_social:
        print(f"   [AI] Analyzing Social Profile for {company_name}...")
        prompt = f"""You are an expert tech consultant. We found this business via their social media.
Business: "{company_name}"
Niche: {niche}
Platform URL: {website_url}

        text = call_gemini(prompt)
        if text:
            score, issues, pitch = 90, "Social media only", ""
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
            return {"score": score, "issues": issues, "pitch": pitch}
        else:
            return {"score": 90, "issues": "Social media only", "pitch": f"Hey! Love the {company_name} content. I build high-converting sites for {niche}s. Want to see a free demo?"}

    else:
        # Business has a website, deeply analyze it
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(website_url, headers=headers, timeout=10)
            page_text = resp.text[:2500]
        except Exception:
            page_text = "Website could not be loaded - likely outdated or broken."

        prompt = f"""You are an elite web application sales consultant. Analyze this website.

Business: "{company_name}" (Type: {niche})
URL: {website_url}
Page Content Extract: {page_text[:1500]}

Respond in EXACTLY this format:
SCORE: [0-100, higher means more opportunity to rebuild]
ISSUES: [Specifically mention 2 critical technical flaws from the content/URL]
PITCH: [A 3-sentence, ultra-professional WhatsApp message. Mention their business name and the specific flaw you found on their website. Offer to build a fast, modern solution to directly increase their revenue. No generic text.]"""

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
    processed = 0
    with SessionLocal() as session:
        new_leads = session.query(Lead).filter(
            Lead.status == "New",
            Lead.ai_score == 0
        ).limit(batch_size).all()

        if not new_leads:
            print("[ENRICHER] Koi nayi leads nahi mili enrichment ke liye.")
            return 0

        print(f"\n[ENRICHER] {len(new_leads)} leads ko Gemini se analyze kar raha hoon...")

        for lead in new_leads:
            print(f"\n[ENRICHER] Analyzing: {lead.company} ({lead.website or 'No Website'})")

            result = analyze_website(
                website_url=lead.website or "",
                company_name=lead.company,
                niche=lead.niche
            )

            lead.ai_score = result["score"]
            lead.notes = f"OBSERVATION: {result['issues']}"
            lead.ai_pitch = result["pitch"]

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

    print(f"\n[ENRICHER] Done! {processed} leads analyzed.")
    return processed


if __name__ == "__main__":
    count = enrich_new_leads(batch_size=10)
    print(f"\n[DONE] {count} leads enrich ho gayi!")

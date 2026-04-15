import asyncio
import re
from playwright.async_api import async_playwright

async def submit_contact_form(website_url, name, email, pitch):
    """
    Automated agent to find a contact form on a website and submit a pitch.
    """
    async with async_playwright() as p:
        # Using stealth-like behavior to avoid simple bot detection
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"[CONTACT-BOT] Visiting {website_url}...")
        try:
            await page.goto(website_url, timeout=45000, wait_until="networkidle")
            
            # 1. Look for Contact Page link
            contact_keywords = ["contact", "get in touch", "connect", "message", "support"]
            links = await page.locator("a").all()
            contact_page_url = None

            for link in links:
                text = (await link.inner_text()).lower()
                href = await link.get_attribute("href") or ""
                if any(kw in text for kw in contact_keywords) or any(kw in href.lower() for kw in contact_keywords):
                    if href.startswith("http"):
                        contact_page_url = href
                    else:
                        # Handle relative paths
                        base = "/".join(website_url.split("/")[:3])
                        contact_page_url = f"{base}/{href.lstrip('/')}"
                    break
            
            if not contact_page_url:
                # Fallback: Just try /contact
                contact_page_url = f"{website_url.rstrip('/')}/contact"

            print(f"[CONTACT-BOT] Navigating to Contact Page: {contact_page_url}")
            await page.goto(contact_page_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(2) # Give it time to render JS forms

            # 2. Identify and Fill Form
            # Heuristics for common field labels/placeholders
            fields = {
                "name": ["name", "full name", "first name", "your name"],
                "email": ["email", "e-mail", "email address", "your email"],
                "message": ["message", "comment", "how can we help", "inquiry", "pitch", "description"]
            }

            found_any = False
            
            # Try filling by Label
            for key, keywords in fields.items():
                val = name if key == "name" else (email if key == "email" else pitch)
                for kw in keywords:
                    try:
                        # search for inputs associated with these labels or placeholders
                        locators = [
                            page.get_by_label(re.compile(kw, re.IGNORECASE)),
                            page.get_by_placeholder(re.compile(kw, re.IGNORECASE)),
                            page.locator(f"input[name*='{kw}']"),
                            page.locator(f"textarea[name*='{kw}']")
                        ]
                        for loc in locators:
                            if await loc.count() > 0 and await loc.first.is_visible():
                                await loc.first.fill(val)
                                found_any = True
                                break
                        if found_any: break
                    except:
                        continue
                found_any = False # reset for next field

            # 3. Submit the form
            submit_buttons = [
                page.get_by_role("button", name=re.compile("submit|send|message|contact", re.IGNORECASE)),
                page.locator("input[type='submit']"),
                page.locator("button[type='submit']")
            ]

            submitted = False
            for btn in submit_buttons:
                if await btn.count() > 0:
                    await btn.first.click()
                    submitted = True
                    print("[CONTACT-BOT] Form submitted successfully!")
                    # Wait a bit for success message
                    await asyncio.sleep(3)
                    break
            
            if not submitted:
                print("[CONTACT-BOT] Could not find a submit button.")
                return False

            await browser.close()
            return True

        except Exception as e:
            print(f"[CONTACT-BOT] Error: {e}")
            await browser.close()
            return False

if __name__ == "__main__":
    # Test run
    asyncio.run(submit_contact_form("https://example.com", "Tushar", "officialtushar@example.com", "Testing our AI pitch bot!"))

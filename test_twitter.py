from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Navigating to Twitter search...")
        try:
            page.goto("https://twitter.com/search?q=web%20design%20needed&f=live", timeout=60000)
            page.wait_for_timeout(5000)
            print(f"URL: {page.url}")
            if "login" in page.url:
                print("REDIRECTED TO LOGIN")
            else:
                print("Stayed on search page (or elsewhere)")
            page.screenshot(path="twitter_test.png")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    test()

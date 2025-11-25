from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("data:text/html,<title>Playwright OK on XAMPP!</title>")
    print("SUCCESS →", page.title())
    browser.close()
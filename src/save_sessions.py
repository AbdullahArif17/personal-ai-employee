from playwright.sync_api import sync_playwright
import json
import os

def save_facebook_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.facebook.com")
        print("Please login to Facebook manually in the browser...")
        print("Press Enter here when you are fully logged in...")
        input()
        cookies = context.cookies()
        os.makedirs("src/sessions", exist_ok=True)
        with open("src/sessions/facebook_cookies.json", "w") as f:
            json.dump(cookies, f)
        print("Facebook session saved!")
        browser.close()

def save_instagram_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.instagram.com")
        print("Please login to Instagram manually in the browser...")
        print("Press Enter here when you are fully logged in...")
        input()
        cookies = context.cookies()
        with open("src/sessions/instagram_cookies.json", "w") as f:
            json.dump(cookies, f)
        print("Instagram session saved!")
        browser.close()

if __name__ == "__main__":
    save_facebook_session()
    save_instagram_session()
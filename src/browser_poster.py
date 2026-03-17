import sys
import json
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

def post_to_facebook(content: str):
    cookies_path = os.path.join(os.path.dirname(__file__), "sessions/facebook_cookies.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # Load saved cookies - skip login entirely
        if os.path.exists(cookies_path):
            with open(cookies_path, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print("Using saved Facebook session...")
        else:
            print("ERROR: No saved session found. Run save_sessions.py first!")
            browser.close()
            return False

        page = context.new_page()

        # Go directly to Facebook page
        page.goto("https://www.facebook.com/profile.php?id=995039850367602")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Take screenshot to see current state
        logs_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Logs"
        logs_dir.mkdir(exist_ok=True)
        screenshot_path = logs_dir / "facebook_debug.png"
        page.screenshot(path=str(screenshot_path))

        # Click create post box
        try:
            page.click('div[aria-label="Create a post"]', timeout=10000)
        except:
            try:
                page.click('div[role="button"]:has-text("Write something")', timeout=10000)
            except:
                try:
                    page.click('[data-pagelet="FeedComposer"]', timeout=10000)
                except:
                    print("Could not find post box - check facebook_debug.png")
                    browser.close()
                    return False

        page.wait_for_timeout(2000)

        # Type content
        page.keyboard.type(content, delay=50)
        page.wait_for_timeout(2000)

        # Click Post button
        try:
            page.click('div[aria-label="Post"]', timeout=10000)
        except:
            try:
                page.click('button:has-text("Post")', timeout=10000)
            except:
                error_screenshot = logs_dir / "facebook_post_error.png"
                page.screenshot(path=str(error_screenshot))
                print("Could not find Post button - check facebook_post_error.png")
                browser.close()
                return False

        page.wait_for_timeout(3000)
        success_screenshot = logs_dir / "facebook_success.png"
        page.screenshot(path=str(success_screenshot))
        print("SUCCESS: Posted to Facebook!")
        browser.close()
        return True

def post_to_instagram(content: str):
    cookies_path = os.path.join(os.path.dirname(__file__), "sessions/instagram_cookies.json")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        if os.path.exists(cookies_path):
            with open(cookies_path, "r") as f:
                cookies = json.load(f)
            context.add_cookies(cookies)
            print("Using saved Instagram session...")
        else:
            print("ERROR: No saved session found. Run save_sessions.py first!")
            browser.close()
            return False

        page = context.new_page()
        page.goto("https://www.instagram.com")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        logs_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Logs"
        logs_dir.mkdir(exist_ok=True)
        screenshot_path = logs_dir / "instagram_debug.png"
        page.screenshot(path=str(screenshot_path))

        # Click create button
        try:
            page.click('svg[aria-label="New post"]', timeout=10000)
        except:
            try:
                page.click('a[href="/create/style/"]', timeout=10000)
            except:
                print("Could not find create button - check instagram_debug.png")
                browser.close()
                return False

        page.wait_for_timeout(2000)
        success_screenshot = logs_dir / "instagram_success.png"
        page.screenshot(path=str(success_screenshot))
        print("SUCCESS: Opened Instagram create post!")
        browser.close()
        return True
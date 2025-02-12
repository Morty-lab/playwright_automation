from playwright.sync_api import sync_playwright
import time
import json

# Facebook credentials (Use environment variables for security)
FB_EMAIL = "aniecabahug69@gmail.com"
FB_PASSWORD = "testpassword"

# Target post URL
POST_URL = "https://www.facebook.com/photo/?fbid=1032406442264985&set=pcb.1032406518931644"

# Headless mode (True for background execution, False to see browser)
HEADLESS_MODE = False

def login_facebook(page):
    """Logs into Facebook."""
    print("Navigating to Facebook login...")
    page.goto("https://www.facebook.com/login")
    
    page.fill("input[name='email']", FB_EMAIL)
    page.fill("input[name='pass']", FB_PASSWORD)
    page.click("button[name='login']")
    
    time.sleep(5)  # Wait for login to complete

def close_popups(page):
    """Closes common Facebook popups."""
    popups = [
        "div[aria-label='Close']",
        "button[aria-label='Close']",
        "button[data-testid='cookie-policy-dialog-accept-button']",
        "button[aria-label='Not Now']",
    ]
    
    for popup in popups:
        try:
            if page.locator(popup).is_visible():
                print(f"Closing popup: {popup}")  
                page.locator(popup).click()
                time.sleep(1)
        except:
            pass  # Ignore errors if the popup isn't present

def load_all_comments(page):
    """Clicks the 'Most relevant' filter and selects 'All comments'."""
    try:
        print("Changing comment filter to 'All comments'...")
        page.get_by_role("button", name="Most relevant").click()
        time.sleep(2)
        page.get_by_role("menuitem", name="All comments Show all").click()
        time.sleep(3)
    except Exception as e:
        print(f"Could not change comment filter: {e}")

def expand_all_comments(page):
    """Expands all comments and replies by clicking 'View more comments' and 'View X reply'."""
    while True:
        view_more = page.get_by_role("button", name="View more comments")
        view_reply = page.locator("button", has_text="View ")
        
        try:
            if view_more.is_visible() and view_more.is_enabled():
                print("Clicking 'View more comments'...")
                view_more.scroll_into_view_if_needed()
                view_more.click()
                time.sleep(3)
            elif view_reply.is_visible() and view_reply.is_enabled():
                print("Clicking 'View X reply'...")
                view_reply.scroll_into_view_if_needed()
                view_reply.click()
                time.sleep(2)
            else:
                break
        except Exception as e:
            print(f"Failed to click button: {e}")
            break

def get_facebook_comments(login=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context()
        page = context.new_page()

        if login:
            login_facebook(page)
            close_popups(page)

        print(f"Navigating to post: {POST_URL}")
        page.goto(POST_URL)
        time.sleep(5)

        close_popups(page)
        load_all_comments(page)
        expand_all_comments(page)

        comment_elements = page.get_by_role("article").all()
        print(f"Found {len(comment_elements)} comments.")

        if not comment_elements:
            print("No comments found! Exiting.")
            browser.close()
            return

        comments_data = {}

        for i, comment in enumerate(comment_elements):
            try:
                full_text = comment.inner_text().strip().split("\n")
                
                if len(full_text) >= 3:
                    user_name = full_text[0].strip()
                    message = full_text[1].strip()
                    time_posted = full_text[2].strip()

                    comments_data[f"comment_{i+1}"] = {
                        "user": user_name,
                        "message": message,
                        "posted": time_posted
                    }
                else:
                    print(f"Skipping malformed comment {i+1}: {full_text}")

            except Exception as e:
                print(f"Error extracting comment {i+1}: {e}")

        browser.close()
        return comments_data

# Run the script (set login=False to skip login)
comments = get_facebook_comments(login=False)

# Save comments to a JSON file
with open('comments.json', 'w') as json_file:
    json.dump(comments, json_file, indent=4)

print("\nFinal Comments Dictionary:")
print(comments)

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
        time.sleep(2)  # Wait for menu to appear
        page.get_by_role("menuitem", name="All comments Show all").click()
        time.sleep(3)  # Wait for comments to reload
    except Exception as e:
        print(f"Could not change comment filter: {e}")

def expand_all_comments(page):
    """Expands all comments and replies by clicking 'View more comments' and 'View X reply'."""
    while True:
        view_more = page.get_by_role("button", name="View more comments")
        view_reply = page.locator("button", has_text="View ")  # Matches 'View X reply'
        
        if view_more.is_visible():
            print("Clicking 'View more comments'...")
            view_more.click()
            time.sleep(3)  # Wait for comments to load
        elif view_reply.is_visible():
            print("Clicking 'View X reply'...")
            view_reply.click()
            time.sleep(2)  # Wait for replies to load
        else:
            break  # Exit loop when no buttons are left

def get_facebook_comments():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context()
        page = context.new_page()

        print("Navigating to Facebook login...")
        page.goto("https://www.facebook.com/login")

        # Login
        page.fill("input[name='email']", FB_EMAIL)
        page.fill("input[name='pass']", FB_PASSWORD)
        page.click("button[name='login']")

        # Wait for login to complete
        time.sleep(5)

        # Close any pop-ups after login
        close_popups(page)

        # Navigate to the post
        print(f"Navigating to post: {POST_URL}")
        page.goto(POST_URL)
        time.sleep(5)  # Wait for comments to load

        # Close pop-ups on the post page
        close_popups(page)

        # Change comment filter to "All comments"
        load_all_comments(page)

        # Expand all comments and replies
        expand_all_comments(page)

        # Locate comments inside the right-hand sidebar
        comment_elements = page.get_by_role("article").all()

        print(f"Found {len(comment_elements)} comments.")

        if not comment_elements:
            print("No comments found! Exiting.")
            browser.close()
            return

        # Store comments in a dictionary
        comments_data = {}

        # Extract and store comments
        for i, comment in enumerate(comment_elements):
            try:
                full_text = comment.inner_text().strip().split("\n")  # Split by new lines
        
                if len(full_text) >= 3:
                    user_name = full_text[0].strip()  # First line is the username
                    message = full_text[1].strip()  # Second line is the message
                    time_posted = full_text[2].strip()  # Third line is the time posted

                    comments_data[f"comment_{i+1}"] = {
                        "user": user_name,
                        "message": message,
                        "posted": time_posted
                    }

                    print(f"\n[COMMENT {i+1}]")
                    print(f"User: {user_name}")
                    print(f"Message: {message}")
                    print(f"Posted: {time_posted}")
                    print("-" * 50)
                else:
                    print(f"Skipping malformed comment {i+1}: {full_text}")

            except Exception as e:
                print(f"Error extracting comment {i+1}: {e}")

        browser.close()

        # Return comments as a dictionary
        return comments_data

# Run the script and store comments in a dictionary
comments = get_facebook_comments()

# Print the dictionary
print("\nFinal Comments Dictionary:")
print(comments)


# Run the script and store comments in a dictionary
comments = get_facebook_comments()

# Save the dictionary to a JSON file
with open('comments.json', 'w') as json_file:
    json.dump(comments, json_file, indent=4)

# Print the dictionary
print("\nFinal Comments Dictionary:")
print(comments)


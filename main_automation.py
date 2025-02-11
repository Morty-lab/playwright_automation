import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.facebook.com/photo/?fbid=1032406442264985&set=pcb.1032406518931644")
    page.get_by_role("button", name="Close").click()
    page.get_by_role("article", name="Comment by ۦۦ ۦۦ 2 days ago").click()
    page.get_by_role("article", name="Comment by Villocero Rhenalyn").click()
    page.get_by_role("article", name="Comment by Meriam Ella Jun 2").click()
    page.get_by_role("article", name="Comment by Glory Ann Bautista").click()
    page.get_by_role("article", name="Comment by Azdonem Thepoj 2").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

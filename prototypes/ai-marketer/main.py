from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from src.seo.layout.structure import (
    validate_description,
    validate_heading,
    validate_semantic_tags,
    validate_title,
)


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect("ws://localhost:3000/chromium/playwright")
        page = browser.new_page()
        page.goto("https://tyumen-soft.ru/")
        page.wait_for_selector("body:not(:empty)")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
        page.screenshot(path="example.png")
        print(page.title())
        soup = BeautifulSoup(content, "html.parser")
        issues = [
            *validate_title(soup),
            *validate_description(soup),
            *validate_heading(soup),
            *validate_semantic_tags(soup),
        ]
        # Close the connection
        browser.close()
        print(issues)


main()

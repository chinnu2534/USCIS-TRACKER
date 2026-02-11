from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText
import time
import os

# YOUR RECEIPT NUMBERS
RECEIPTS = {
    "You": "IOE9401077524",
    "Sister": "IOE9236537298"
}

# YOUR EMAIL
EMAIL_FROM = "abhinav.unitedstates@gmail.com"
EMAIL_TO = "sunny70361@gmail.com"
EMAIL_PASS = os.getenv("EMAIL_PASS")


def get_status(receipt):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
        )

        page = context.new_page()

        # Go to site
        page.goto(
            "https://egov.uscis.gov/casestatus/landing.do",
            timeout=60000
        )

        # Wait for Cloudflare / page load
        page.wait_for_timeout(15000)

        # Wait until input appears
        page.wait_for_selector("input[name='receipt_number']", timeout=60000)

        # Fill receipt
        page.fill("input[name='receipt_number']", receipt)

        # Click submit
        page.click("button[type='submit']")

        # Wait for result
        page.wait_for_timeout(10000)

        # Get status
        status = page.locator("h1").first.inner_text()
        details = page.locator("p").first.inner_text()

        browser.close()

        return status, details



def send_email(report):
    msg = MIMEText(report)

    msg["Subject"] = "Daily USCIS Status"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASS)
        server.send_message(msg)


def main():
    report = "USCIS Daily Status Report\n\n"

    for name, receipt in RECEIPTS.items():
        status, details = get_status(receipt)

        report += f"""
{name}:
{status}
{details}

---------------------
"""

        time.sleep(5)

    send_email(report)


if __name__ == "__main__":
    main()

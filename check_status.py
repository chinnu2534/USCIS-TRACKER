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
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://egov.uscis.gov/casestatus/landing.do")
        page.wait_for_timeout(8000)

        page.fill("#receipt_number", receipt)
        page.click("button[type='submit']")

        page.wait_for_timeout(8000)

        status = page.locator("h1").inner_text()
        details = page.locator("p").inner_text()

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

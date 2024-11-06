import csv
import re
import os
import argparse
import time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from uuid import uuid4
from const import API_URL
from dotenv import load_dotenv

load_dotenv()


class Mailer:
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self, csv_file, department_code, subject, body_template):
        self.email_id = str(uuid4())
        self.csv_file = csv_file
        self.department_code = department_code
        self.subject = subject
        self.body_template = body_template
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = os.getenv("EMAIL_USERNAME")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipients = []
        self.batch_size = 10  # Number of emails to send before delay
        self.delay = 2  # Delay time in seconds

    def is_valid_email(self, email):
        return re.match(self.EMAIL_REGEX, email) is not None

    def parse_csv(self):
        with open(self.csv_file, mode="r") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                if not self.is_valid_email(row["email"]):
                    print(f"Invalid email found and skipped: {row['email']}")
                    continue

                # Case insensitive
                if (
                    self.department_code.lower() == "all"
                    or row["department_code"].lower() == self.department_code.lower()
                ):
                    self.recipients.append(
                        {
                            "email": row["email"],
                            "name": row["name"],
                            "department_code": row["department_code"],
                        }
                    )

    def display_recipients(self):
        if not self.recipients:
            print("\nNo emails with matching department code.")
        else:
            print("\nValid recipients:")
            for recipient in self.recipients:
                print(
                    f"Email: {recipient['email']}, Name: {recipient['name']}, Department: {recipient['department_code']}"
                )

    def personalize_content(self, recipient):
        body_lines = self.body_template.split("\n")
        for idx, line in enumerate(body_lines):
            if "</body>" in line:
                body_lines.insert(
                    idx,
                    f'<img src="{API_URL}tracking/pixel?recipient_email={recipient['email']}&email_id={self.email_id}" alt="" style="display:none;">',
                )
                break

        body = (
            "\n".join(body_lines)
            .replace("#name#", recipient["name"])
            .replace("#department#", recipient["department_code"])
        )

        return body

    def send_email(self, recipient):
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = recipient["email"]
        msg["Subject"] = self.subject

        body = self.personalize_content(recipient)
        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, recipient["email"], msg.as_string())
            print(f"Email sent to {recipient['email']}")
            self.insert_into_email_history(
                recipient["email"], recipient["department_code"]
            )
            return True
        except Exception as e:
            print(f"Failed to send email to {recipient['email']}: {e}")
            return False

    def send_emails(self):
        for index, recipient in enumerate(self.recipients):
            self.send_email(recipient)

            # Check if the batch limit is reached
            if (index + 1) % self.batch_size == 0:
                # Add delay if reached
                time.sleep(self.delay)

    def insert_into_email_history(self, email, department_code):
        request_data = {
            "email_id": self.email_id,
            "recipient_email": email,
            "department_code": department_code,
            "email_subject": self.subject,
        }

        try:
            resp = requests.post(
                f"{API_URL}email-history",
                json=request_data,
            )
        except requests.exceptions.RequestException as e:
            print(f"insert_into_email_history error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Smart Mailer Program")
    parser.add_argument("csvfile")
    parser.add_argument("department_code")
    parser.add_argument("subject")
    parser.add_argument("body_template")

    args = parser.parse_args()
    csv_file = args.csvfile
    department_code = args.department_code
    subject = args.subject
    body_template_file = args.body_template

    # Read the html template from a .txt file
    with open(body_template_file, "r") as f:
        body_template = f.read()

    # Initialize Mailer class
    mailer = Mailer(csv_file, department_code, subject, body_template)

    # Parse CSV
    mailer.parse_csv()

    # Print recipients
    mailer.display_recipients()

    # Send emails to recipients
    mailer.send_emails()


if __name__ == "__main__":
    # Usage
    # python mailer.py maildata.csv <Department Code> <Subject> <body file>.txt
    main()

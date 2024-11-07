import csv
import sys
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
from utils import encode_key

from get_info import get_email_count_by_department, get_tracking_information

load_dotenv()


class Mailer:
    """
    Class to handle the bulk email sending process, including recipient validation,
    email content personalization, and logging of sent emails.
    """

    # Define a regular expression for email validation.
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self, csv_file, department_code, subject, body_template):
        """
        Initialize Mailer with provided configurations for email sending.
        """
        self.email_id = str(uuid4()) # Unique ID for each email session
        self.csv_file = csv_file 
        self.department_code = department_code
        self.subject = subject
        self.body_template = body_template
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587 # SMTP port for TLS
        self.username = os.getenv("EMAIL_USERNAME") # Email sender credentials
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipients = []
        self.batch_size = 25  # Number of emails to send before delay
        self.delay = 10  # Delay time in seconds between batches
        self.retry_attempts = 3  # Maximum retry attempts for each email
        self.backoff_factor = 2  # Exponential backoff factor for retries

    def is_valid_email(self, email):
        """
        Check if an email address is valid.
        """
        return re.match(self.EMAIL_REGEX, email) is not None

    def parse_csv(self):
        """
        Parse the CSV file and filter recipients based on the department code.
        Adds valid recipients to the self.recipients list.
        """
        with open(self.csv_file, mode="r") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                if not self.is_valid_email(row["email"]):
                    print(f"Invalid email found and skipped: {row['email']}")
                    continue

                # Add recipient if department code matches or if "ALL" is specified (case insensitive).
                if (self.department_code.upper() == "ALL" or 
                    row["department_code"].upper() == self.department_code.upper()):
                    self.recipients.append(
                        {
                        "email": row["email"],
                        "name": row["name"],
                        "department_code": row["department_code"].upper(),
                        }
                    )

    def display_recipients(self):
        """
        Display the list of valid recipients.
        """

        if not self.recipients:
            print("\nNo emails with matching department code.")
        else:
            print("\nValid recipients:")
            for recipient in self.recipients:
                print(
                    f"Email: {recipient['email']}, Name: {recipient['name']}, Department: {recipient['department_code']}"
                    )

    def personalize_content(self, recipient):
        """
        Customize the email body template for each recipient.
        """
        body_lines = self.body_template.split("\n")

        # Insert tracking pixel to html body
        for idx, line in enumerate(body_lines):
            if "</body>" in line:
                body_lines.insert(
                    idx,
                    f'<img src="{API_URL}tracking/pixel?recipient_email={recipient['email']}&email_id={self.email_id}" alt="" style="display:none;">',
                )
                break
        # Replace placeholders in template with recipient's info.
        body = (
            "\n".join(body_lines)
            .replace("#name#", recipient["name"])
            .replace("#department#", recipient["department_code"])
        )

        return body

    def send_email(self, recipient):
        """
        Prepare and send an email to a single recipient, with retry logic.
        """    
        
        msg = MIMEMultipart()
        msg["From"] = self.username
        msg["To"] = recipient["email"]
        msg["Subject"] = self.subject
        
        body = self.personalize_content(recipient)
        msg.attach(MIMEText(body, "html"))

        # Attempt to send the email, with retries on failure.
        for attempt in range(self.retry_attempts):
            try:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.sendmail(self.username, recipient["email"], msg.as_string())
                print(f"Email sent to {recipient['email']}")
                self.insert_into_email_history(recipient["email"], recipient["department_code"])
                return True
            
            except Exception as e:
                print(f"Failed to send email to {recipient['email']} on attempt {attempt + 1}: {e}")

                if attempt < self.retry_attempts - 1:

                    # The delay between retries increases exponentially based on the retry attempt number.
                    time.sleep(self.delay * (self.backoff_factor ** attempt))  

        # Return False if email fails to send on all attempts. 
        return False

    def send_emails(self):
        """
        Send emails to all recipients in the list, applying a batching delay mechanism.
        """

        for index, recipient in enumerate(self.recipients):
            success = self.send_email(recipient)
            
            if not success:
                print(f"Failed sending email to {recipient['email']} after {self.retry_attempts} attempts.")
            
            if (index + 1) % self.batch_size == 0:
                # Add delay if batch size is reached
                time.sleep(self.delay)

    def insert_into_email_history(self, email, department_code):
        """
        Log sent emails by sending data to the database.
        """
        
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
                headers={"Authorization": f"Bearer {os.environ.get("APP_KEY")}"},
            )
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"insert_into_email_history error: {e}")

def main():
    """
    Main function to run the mailer program, which can send emails or retrieve analytics.
    """

    parser = argparse.ArgumentParser(description="Smart Mailer Program")

    # Add a positional argument for the mode with choices "send" or "analytics".
    # "send" mode sends emails, while "analytics" retrieves email analytics.
    parser.add_argument(
        "mode",
        choices=["send", "analytics"],
        help="Choose the mode: 'send' to send an email, 'get' to get email analytics",
    )

    # Parse the mode argument from the command line.
    args = parser.parse_args(sys.argv[1:2])
    mode = args.mode

    # If the mode is "analytics", fetch and display email tracking information and exit. 
    if mode == "analytics":
        try:
            print(get_tracking_information())
            print("\n")
            print(get_email_count_by_department())
            exit(0)
        except Exception as e:
            print(f"Error in retrieving data")
            exit(1)

    # For "send" mode, create a new argument parser for sending emails.
    parser = argparse.ArgumentParser(description="Send Emails Parser")

    # Define arguments required in "send" mode.
    parser.add_argument(
        "mode",
        choices=["send"],
        help="Choose the mode: 'send' to send an email, 'get' to get email analytics",
    )
    
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
    # To send emails: python mailer.py send maildata.csv <Department Code> <Subject> <body file>.txt
    # To fetch analytics: python mailer.py analytics
    main()

import csv
import re
import argparse

class Mailer:
    # Regular expression pattern to validate an email address
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, csv_file, department_code):
        self.csv_file = csv_file
        self.department_code = department_code
        self.recipients = []

    def is_valid_email(self, email):
        """Check if the email address is in valid format."""
        return re.match(self.EMAIL_REGEX, email) is not None

    def parse_csv(self):
        """Parse the CSV file and filter recipients based on the department code."""
        with open(self.csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                # Check if email is valid
                if not self.is_valid_email(row['email']):
                    print(f"Invalid email found and skipped: {row['email']}")
                    continue

                # Filter by department code
                if self.department_code.lower() == "all" or row['department_code'].lower() == self.department_code.lower():
                    self.recipients.append({
                        'email': row['email'],
                        'name': row['name'],
                        'department_code': row['department_code']
                    })

    def display_recipients(self):
        
        if not self.recipients:
            print("\nNo emails with matching department code.")
        else: 
            print("\nValid recipients:")     
            for recipient in self.recipients:
                print(f"Email: {recipient['email']}, Name: {recipient['name']}, Department: {recipient['department_code']}")

def main():
    # Set up argument parsing
    # Usage: python mailer.py <department code>
    # OR to get all emails: python mailer.py all
    parser = argparse.ArgumentParser(description="Smart Mailer Program")
    parser.add_argument("csvfile")
    parser.add_argument("department_code")
    
    # Parse the arguments
    args = parser.parse_args()
    csv_file = args.csvfile
    department_code = args.department_code

    # Initialize Mailer class
    mailer = Mailer(csv_file, department_code)
    
    # Parse CSV 
    mailer.parse_csv()

    # Print recipients 
    mailer.display_recipients()

if __name__ == "__main__":
    main()

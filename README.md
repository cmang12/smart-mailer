## Smart Mailer Program

### Overview

The `Smart Mailer Program` allows you to:
1. Send emails to a list of recipients to specific departments from a CSV file.
2. Retrieve email analytics, which provides a tracking counter for the number of users who opened the email and the number of emails sent by department code.


### Architecture Diagram
![image](https://github.com/user-attachments/assets/482cc5c6-f18b-4f66-b2b5-9823307cde87)
This CLI program is designed to be used with the backend available at [smart-mailer-backend](https://github.com/gwynethguo/smart-mailer-backend/).


### Prerequisites

1. **Python 3.x**: Ensure Python is installed.
2. **Dependencies**: Install required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```
3. **Environment Variables**: Set up a `.env` file in the root directory with the following values:
    ```env
    EMAIL_USERNAME=<your_email_username>
    EMAIL_PASSWORD=<your_email_password>
    APP_KEY=<your_app_key>
    ```

### Usage

The program supports two modes: `send` and `analytics`.

#### 1. Send Mode

To send an email, use the `send` mode with these arguments:
- `csvfile`: Path to the CSV file with recipient data.
- `department_code`: Code of the department sending the email.
- `subject`: Subject line of the email.
- `body_template`: Path to the body template file.

**Example:**
```bash
python mailer.py send maildata.csv SOC "[NUS Career Fair] Join us tomorrow!" body.txt
```

#### 2. Analytics Mode

To retrieve email analytics, use the `analytics` mode. No additional arguments are required.

**Example:**
```bash
python mailer.py analytics
```
### Error Handling

If an error occurs during data retrieval in `analytics` mode, an error message will be displayed, and the program will exit with a non-zero code.

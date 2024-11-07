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

#### Example Output for Analytics Mode

When running the `analytics` mode, the program provides two sections:

1. **Email Open Count**: This section tracks how many users opened each email. It provides details such as:
   - `count`: The number of users who opened the email.
   - `email_id`: A unique identifier for each email.
   - `email_subject`: The subject of the email.
   - `latest_created_at`: The timestamp of the most recent open event.

   **Example:**
   ```plaintext
   EMAIL OPEN COUNT
   +---------+--------------------------------------+-------------------------+-------------------------------+
   |   count | email_id                             | email_subject           | latest_created_at             |
   +=========+======================================+=========================+===============================+
   |       2 | 099277f6-aa70-4d99-bc5a-478e9d7f77cb | Monthly Report           | Wed, 06 Nov 2024 11:35:08 GMT |
   +---------+--------------------------------------+-------------------------+-------------------------------+
   |       3 | f10881d0-3333-41ae-8231-d0993e8937cd | New Product Launch       | Wed, 06 Nov 2024 11:16:03 GMT |
   +---------+--------------------------------------+-------------------------+-------------------------------+
   |       1 | 7a37b701-ddcb-41aa-a9eb-30efcf645f94 | Weekly Update            | Wed, 06 Nov 2024 10:02:04 GMT |
   +---------+--------------------------------------+-------------------------+-------------------------------+
   ```
   In this example:
    - The email with `email_id = f10881d0-3333-41ae-8231-d0993e8937cd` (subject: `New Product Launch`) was opened by 3 users, with the last open recorded at `Wed, 06 Nov 2024 11:16:03 GMT`.
    - The email with `email_id = 7a37b701-ddcb-41aa-a9eb-30efcf645f94` (subject: `Weekly Update`) was opened by 1 user.

2. **Email Count by Department**: This section shows the total number of emails sent by each department code. The `ALL` department is excluded from the output.

   **Example:**
   ```plaintext
   EMAIL COUNT BY DEPARTMENT
   +---------+-------------------+
   |   count | department_code   |
   +=========+===================+
   |       5 | eng               |
   +---------+-------------------+
   |      14 | SOC               |
   +---------+-------------------+
   |       2 | MED               |
   +---------+-------------------+
   |       3 | CEG               |
   +---------+-------------------+
   |       8 | FASS              |
   +---------+-------------------+
   ```
   In this case:
    - The department `SOC` sent the most emails (14).
    - The department `FASS` sent 8 emails.

### Error Handling

If an error occurs during data retrieval in `analytics` mode, an error message will be displayed, and the program will exit with a non-zero code.

# Bulk Recruiter Email Sender

This Jupyter Notebook is designed **for educational purposes only**. It demonstrates how to automate the process of sending personalized emails to multiple recruiters using Python. The goal is to help job seekers efficiently reach out to potential employers and improve their chances of getting noticed during the job search.

## Purpose

The primary use case of this script is to:

- **Send bulk emails to recruiters** with personalized messages.
- **Attach resumes automatically**.
- **Avoid duplicates** by logging sent emails.
- **Introduce random delays** between batches to mimic human behavior.

## Features

- Reads recruiter info (email, name, company) from a CSV file.
- Sends customized emails using Gmail SMTP.
- Attaches a predefined resume to each email.
- Logs all sent emails to prevent resending.
- Introduces randomized batch delays between email groups for throttling.

## Files

- `Cold Mail Send.ipynb` – The main notebook to run the email automation.
- `recipients.csv` – Input file with recipient details (`email`, `first_name`, `company`).
- `Varunprakash_Shanmugam_Resume.pdf` – Resume to be attached.
- `sent_emails_log.csv` – Auto-generated log of sent emails, this log help you by avoid sending same email again.

## Disclaimer

> This tool is intended **solely for educational purposes** to understand Python-based email automation. The author does **not endorse or condone spamming or misuse** of this tool. Use responsibly and adhere to applicable laws and platform terms of service when sending emails.

## Getting Started

1. Install dependencies:
   ```bash
   pip install pandas

2. Configure your email and recipient details:

- In the notebook, update the following constants: (Refer: https://medium.com/@varunprakashs/how-to-create-an-app-password-in-google-for-less-secure-apps-4828e67693cd)
  
  ```
  EMAIL_ADDRESS = "your_email@gmail.com"
  EMAIL_PASSWORD = "your_app_password"  # Use a Gmail App Password

3. Create a recipients.csv file with the following format (no headers required):

John,Amazon,example@email.com

Jane,Google,jane.doe@company.com



## Recommended platform to run this: Anaconda Cloud or GitHub CodeSpaces.

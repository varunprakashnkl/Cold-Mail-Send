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
- **Weekly security monitoring** to check for potential security issues.

## Files

- `Cold Mail Send.ipynb` – The main notebook to run the email automation.
- `secure_email_sender.py` - A more secure Python script version with enhanced security features.
- `recipients.csv` – Input file with recipient details (`email`, `first_name`, `company`).
- `Varunprakash_Shanmugam_Resume.pdf` – Resume to be attached.
- `sent_emails_log.csv` – Auto-generated log of sent emails, this log help you by avoid sending same email again.
- `.env.example` - Template for environment variables to store credentials securely.
- `security_monitor.py` - Script to check for security issues in the codebase.

## Security Features

This repository includes several security enhancements:

1. **Weekly Automated Security Scans**: GitHub Actions workflow runs security checks every Monday.
2. **Environment Variables**: Sensitive information is stored in environment variables instead of hardcoded in the script.
3. **Input Validation**: Email addresses and file paths are validated before use.
4. **Logging**: Comprehensive logging with privacy protection (email hashing).
5. **Manual Security Monitoring**: Run `python security_monitor.py` to check for security issues anytime.

## Disclaimer

> This tool is intended **solely for educational purposes** to understand Python-based email automation. The author does **not endorse or condone spamming or misuse** of this tool. Use responsibly and adhere to applicable laws and platform terms of service when sending emails.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your environment:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. Create a recipients.csv file with the following format (no headers required):
   ```
   example@email.com,John,Amazon
   jane.doe@company.com,Jane,Google
   ```

4. Run the secure version:
   ```bash
   python secure_email_sender.py
   ```

5. Run security checks:
   ```bash
   python security_monitor.py
   ```

## Security Monitoring

The repository includes automated weekly security checks that:

1. Scan for hardcoded credentials
2. Check for common security vulnerabilities
3. Validate input handling
4. Check for outdated dependencies

Security reports are generated and stored as artifacts in GitHub Actions.

## Recommended platform to run this: Anaconda Cloud or GitHub CodeSpaces.

#!/usr/bin/env python3
"""
Secure Email Sender Script
This script sends personalized emails to recruiters with security enhancements.
"""

import smtplib
import pandas as pd
import time
import os
import random
import re
import hashlib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("email_sender.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Load environment variables from .env file if it exists
load_dotenv()

# Constants - Load from environment variables or prompt user
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# If environment variables are not set, prompt the user
if not EMAIL_ADDRESS:
    EMAIL_ADDRESS = input("Enter your email address: ")
if not EMAIL_PASSWORD:
    from getpass import getpass
    EMAIL_PASSWORD = getpass("Enter your app password: ")

RESUME_PATH = os.getenv("RESUME_PATH", "RESUME_FILE_NAME.pdf") 
RESUME_FILENAME = os.getenv("RESUME_FILENAME", "RESUME_FILE_NAME.pdf")
SENT_LOG_FILE = "sent_emails_log.csv"
RECIPIENTS_CSV = "recipients.csv"

# Security check: Validate that required files exist
def validate_files():
    if not os.path.exists(RESUME_PATH):
        logger.error(f"Resume file not found: {RESUME_PATH}")
        return False
    
    if not os.path.exists(RECIPIENTS_CSV):
        logger.error(f"Recipients CSV file not found: {RECIPIENTS_CSV}")
        return False
    
    return True

# Security check: Validate email format
def is_valid_email(email):
    pattern = r'^[\w\.-]+@([\w\-]+\.)+[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))

# Security function: Hash email addresses for logging
def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()[:16]

# Load and validate recipients
def load_recipients():
    try:
        df = pd.read_csv(RECIPIENTS_CSV, header=None, names=['email', 'first_name', 'company'])
        
        # Validate email format
        invalid_emails = [email for email in df['email'] if not is_valid_email(email)]
        if invalid_emails:
            logger.warning(f"Found {len(invalid_emails)} invalid email formats in the CSV file")
            for email in invalid_emails[:5]:  # Show first 5 invalid emails
                logger.warning(f"Invalid email format: {email}")
            df = df[df['email'].apply(is_valid_email)]
        
        return df
    except Exception as e:
        logger.error(f"Error loading recipients: {e}")
        return pd.DataFrame()

# Load sent emails log
def load_sent_log():
    if os.path.exists(SENT_LOG_FILE):
        try:
            sent_log_df = pd.read_csv(SENT_LOG_FILE)
            return set(sent_log_df['email'])
        except Exception as e:
            logger.error(f"Error loading sent emails log: {e}")
            return set()
    else:
        return set()

# Email content
def create_email_body(first_name, company):
    return f"""Dear {first_name},

I hope this message finds you well.

My name is Varunprakash Shanmugam, and I recently graduated from City University of Seattle with a Master's degree in Computer Science. I am writing to express my strong interest in potential opportunities at {company}, particularly in Cloud Engineering/DevOps/IT Support roles.

I have practical experience designing and implementing cloud infrastructure solutions. For instance, I architected multi-cloud solutions using CloudFormation and developed DevOps pipelines integrating EC2, S3, and Lambda services. My experience also includes architecting and deploying distributed systems using Kubernetes and implementing CI/CD pipelines with tools like GitLab CI and Jenkins. I'm proficient in technologies such as AWS, Azure, Docker, Kubernetes, Cloud Formation, and Python.

Thank you for your time and consideration. I look forward to the possibility of connecting.

Best regards,  
Varunprakash Shanmugam  
https://linkedin.com/in/varunprakashs
"""

# Update sent emails log
def update_sent_log(log):
    try:
        if os.path.exists(SENT_LOG_FILE):
            prev_log = pd.read_csv(SENT_LOG_FILE)
            new_entries = pd.DataFrame([entry for entry in log if entry['status'] == 'Success'])
            updated_log = pd.concat([prev_log, new_entries], ignore_index=True)
        else:
            updated_log = pd.DataFrame([entry for entry in log if entry['status'] == 'Success'])

        updated_log.to_csv(SENT_LOG_FILE, index=False)
        logger.info("Sent email log updated successfully")
    except Exception as e:
        logger.error(f"Error updating sent emails log: {e}")

# Main function
def send_emails():
    # Validate required files
    if not validate_files():
        return
    
    # Load recipients
    df = load_recipients()
    if df.empty:
        logger.error("No valid recipients found. Exiting.")
        return
    
    # Load sent emails log
    already_sent = load_sent_log()
    
    # Load resume
    try:
        with open(RESUME_PATH, 'rb') as f:
            resume_data = f.read()
    except Exception as e:
        logger.error(f"Error reading resume file: {e}")
        return
    
    # Connect to SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("Successfully connected to SMTP server")
    except smtplib.SMTPAuthenticationError:
        logger.error("Authentication failed. Please check your email credentials.")
        return
    except Exception as e:
        logger.error(f"Error connecting to SMTP server: {e}")
        return
    
    # Send emails
    log = []
    email_counter = 0
    batch_size = random.randint(3, 7)
    total_sent = 0
    total_skipped = 0
    
    # Security check: Set maximum emails per session
    MAX_EMAILS_PER_SESSION = 50
    
    for index, row in df.iterrows():
        # Security check: Limit total emails per session
        if total_sent >= MAX_EMAILS_PER_SESSION:
            logger.warning(f"Maximum email limit reached ({MAX_EMAILS_PER_SESSION}). Stopping for safety.")
            break
            
        recipient_email = row['email']
        first_name = row['first_name']
        company = row['company']

        if recipient_email in already_sent:
            logger.info(f"Skipped (already sent): {hash_email(recipient_email)}")
            total_skipped += 1
            continue

        msg = MIMEMultipart()
        msg['From'] = formataddr(("Varunprakash Shanmugam", EMAIL_ADDRESS))
        msg['To'] = recipient_email
        msg['Subject'] = f"Looking for Cloud Engineering / DevOps Opportunities at {company}"

        body = create_email_body(first_name, company)
        msg.attach(MIMEText(body, 'plain'))

        part = MIMEApplication(resume_data, Name=RESUME_FILENAME)
        part['Content-Disposition'] = f'attachment; filename="{RESUME_FILENAME}"'
        msg.attach(part)

        try:
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
            logger.info(f"Email sent to {hash_email(recipient_email)}")
            log.append({"email": recipient_email, "status": "Success", "error": ""})
            total_sent += 1
        except Exception as e:
            logger.error(f"Failed to send email to {hash_email(recipient_email)}: {e}")
            log.append({"email": recipient_email, "status": "Failed", "error": str(e)})

        # Per-email random delay
        delay = random.uniform(2, 12)
        logger.info(f"Sleeping {delay:.2f}s before next email...")
        time.sleep(delay)

        # Batch pause logic
        email_counter += 1
        if email_counter >= batch_size:
            batch_delay = random.randint(30, 90)
            logger.info(f"Batch limit reached. Sleeping {batch_delay}s to avoid spam detection...")
            time.sleep(batch_delay)
            email_counter = 0
            batch_size = random.randint(3, 7)

    server.quit()
    logger.info(f"Email sending complete. Total sent: {total_sent}, Total skipped: {total_skipped}")
    
    # Update sent emails log
    update_sent_log(log)

if __name__ == "__main__":
    send_emails()
#!/usr/bin/env python3
"""
Cold Mail Sender - Automated Bulk Email Tool for Recruiters
Educational purposes only. Use responsibly.
"""

import smtplib
import pandas as pd
import time
import os
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formataddr
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Constants - Load from environment variables or use defaults
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")
RESUME_PATH = os.getenv("RESUME_PATH", "your_resume.pdf")
RESUME_FILENAME = os.getenv("RESUME_FILENAME", "Resume.pdf")
SENT_LOG_FILE = os.getenv("SENT_LOG_FILE", "sent_emails_log.csv")
RECIPIENTS_CSV = os.getenv("RECIPIENTS_CSV", "recipients.csv")
SENDER_NAME = os.getenv("SENDER_NAME", "Your Name")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "https://linkedin.com/in/your-profile")

# Email personalization (optional customization)
UNIVERSITY = os.getenv("UNIVERSITY", "City University of Seattle")
DEGREE = os.getenv("DEGREE", "Master's degree in Computer Science")
JOB_ROLES = os.getenv("JOB_ROLES", "Cloud Engineering/DevOps/IT Support")

# Rate limiting configuration
MIN_BATCH_SIZE = int(os.getenv("MIN_BATCH_SIZE", "3"))
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "7"))
MIN_EMAIL_DELAY = float(os.getenv("MIN_EMAIL_DELAY", "2"))
MAX_EMAIL_DELAY = float(os.getenv("MAX_EMAIL_DELAY", "12"))
MIN_BATCH_DELAY = int(os.getenv("MIN_BATCH_DELAY", "30"))
MAX_BATCH_DELAY = int(os.getenv("MAX_BATCH_DELAY", "90"))


def create_email_body(first_name, company):
    """Create personalized email body"""
    return f"""Dear {first_name},

I hope this message finds you well.

My name is {SENDER_NAME}, and I recently graduated from {UNIVERSITY} with a {DEGREE}. I am writing to express my strong interest in potential opportunities at {company}, particularly in {JOB_ROLES} roles.

I have practical experience designing and implementing cloud infrastructure solutions. For instance, I architected multi-cloud solutions using CloudFormation and developed DevOps pipelines integrating EC2, S3, and Lambda services. My experience also includes architecting and deploying distributed systems using Kubernetes and implementing CI/CD pipelines with tools like GitLab CI and Jenkins. I'm proficient in technologies such as AWS, Azure, Docker, Kubernetes, Cloud Formation, and Python.

Thank you for your time and consideration. I look forward to the possibility of connecting.

Best regards,  
{SENDER_NAME}  
{LINKEDIN_URL}
"""


def validate_configuration():
    """Validate that all required configuration is present"""
    errors = []
    
    if EMAIL_ADDRESS == "your_email@gmail.com" or not EMAIL_ADDRESS:
        errors.append("EMAIL_ADDRESS not configured")
    
    if EMAIL_PASSWORD == "your_app_password" or not EMAIL_PASSWORD:
        errors.append("EMAIL_PASSWORD not configured")
    
    if not os.path.exists(RESUME_PATH):
        errors.append(f"Resume file not found: {RESUME_PATH}")
    
    if not os.path.exists(RECIPIENTS_CSV):
        errors.append(f"Recipients CSV not found: {RECIPIENTS_CSV}")
    
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease update your configuration and try again.")
        print("You can create a .env file based on .env.example")
        return False
    
    return True


def main():
    """Main function to send bulk emails"""
    print("Cold Mail Sender - Starting...")
    print("=" * 50)
    
    # Validate configuration
    if not validate_configuration():
        return
    
    # Load recipients
    try:
        df = pd.read_csv(RECIPIENTS_CSV, header=None, names=['first_name', 'company', 'email'])
        print(f"Loaded {len(df)} recipients from {RECIPIENTS_CSV}")
    except Exception as e:
        print(f"Error loading recipients: {e}")
        return
    
    # Load sent emails log
    if os.path.exists(SENT_LOG_FILE):
        sent_log_df = pd.read_csv(SENT_LOG_FILE)
        already_sent = set(sent_log_df['email'])
        print(f"Found {len(already_sent)} previously sent emails")
    else:
        already_sent = set()
        print("No previous log found - starting fresh")
    
    # Load resume
    try:
        with open(RESUME_PATH, 'rb') as f:
            resume_data = f.read()
        print(f"Loaded resume: {RESUME_PATH}")
    except Exception as e:
        print(f"Error loading resume: {e}")
        return
    
    # Connect to SMTP server
    print("\nConnecting to Gmail SMTP server...")
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print("Successfully authenticated with Gmail")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed. Please check your email credentials.")
        print("Make sure you're using a Gmail App Password, not your regular password.")
        return
    except Exception as e:
        print(f"Error connecting to SMTP server: {e}")
        return
    
    # Send emails
    print("\nStarting to send emails...")
    print("=" * 50)
    
    email_counter = 0
    batch_size = random.randint(MIN_BATCH_SIZE, MAX_BATCH_SIZE)
    sent_count = 0
    skipped_count = 0
    failed_count = 0
    
    for index, row in df.iterrows():
        recipient_email = row['email']
        first_name = row['first_name']
        company = row['company']
        
        if recipient_email in already_sent:
            print(f"[{index + 1}/{len(df)}] SKIPPED (already sent): {recipient_email}")
            skipped_count += 1
            continue
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = formataddr((SENDER_NAME, EMAIL_ADDRESS))
        msg['To'] = recipient_email
        msg['Subject'] = f"Looking for Cloud Engineering / DevOps Opportunities at {company}"
        
        # Set priority headers
        msg.add_header('X-Priority', '1')
        msg.add_header('X-MSMail-Priority', 'High')
        msg.add_header('Importance', 'High')
        
        # Add body
        body = create_email_body(first_name, company)
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        part = MIMEApplication(resume_data, Name=RESUME_FILENAME)
        part['Content-Disposition'] = f'attachment; filename="{RESUME_FILENAME}"'
        msg.attach(part)
        
        # Send email
        try:
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
            print(f"[{index + 1}/{len(df)}] SUCCESS: Email sent to {recipient_email}")
            
            # Log success immediately
            pd.DataFrame([{"email": recipient_email}]).to_csv(
                SENT_LOG_FILE, mode='a', header=not os.path.exists(SENT_LOG_FILE), index=False
            )
            already_sent.add(recipient_email)
            sent_count += 1
        except Exception as e:
            print(f"[{index + 1}/{len(df)}] FAILED: {recipient_email} - {e}")
            failed_count += 1
        
        # Per-email random delay
        delay = random.uniform(MIN_EMAIL_DELAY, MAX_EMAIL_DELAY)
        print(f"  Sleeping {delay:.2f}s before next email...")
        time.sleep(delay)
        
        # Batch pause logic
        email_counter += 1
        if email_counter >= batch_size:
            batch_delay = random.randint(MIN_BATCH_DELAY, MAX_BATCH_DELAY)
            print(f"\n  *** Batch limit reached. Sleeping {batch_delay}s to avoid spam detection... ***\n")
            time.sleep(batch_delay)
            email_counter = 0
            batch_size = random.randint(MIN_BATCH_SIZE, MAX_BATCH_SIZE)
    
    # Close connection
    server.quit()
    
    # Print summary
    print("\n" + "=" * 50)
    print("Email Campaign Summary:")
    print(f"  Total recipients: {len(df)}")
    print(f"  Sent: {sent_count}")
    print(f"  Skipped (already sent): {skipped_count}")
    print(f"  Failed: {failed_count}")
    print("=" * 50)
    print("\nAll emails processed. Log file updated after each successful send.")


if __name__ == "__main__":
    main()
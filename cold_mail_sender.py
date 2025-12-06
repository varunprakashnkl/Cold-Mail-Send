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
import re
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

# Email behavior
EMAIL_PRIORITY = os.getenv("EMAIL_PRIORITY", "normal")  # 'high' or 'normal'

# Email personalization (optional customization)
UNIVERSITY = os.getenv("UNIVERSITY", "City University of Seattle")
DEGREE = os.getenv("DEGREE", "Master's degree in Computer Science")
JOB_ROLES = os.getenv("JOB_ROLES", "Cloud Engineering/DevOps/IT Support")

# Rate limiting configuration
try:
    MIN_BATCH_SIZE = int(os.getenv("MIN_BATCH_SIZE", "3"))
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "7"))
    MIN_EMAIL_DELAY = float(os.getenv("MIN_EMAIL_DELAY", "2"))
    MAX_EMAIL_DELAY = float(os.getenv("MAX_EMAIL_DELAY", "12"))
    MIN_BATCH_DELAY = int(os.getenv("MIN_BATCH_DELAY", "30"))
    MAX_BATCH_DELAY = int(os.getenv("MAX_BATCH_DELAY", "90"))
    
    # Validate ranges
    if MIN_BATCH_SIZE < 1 or MAX_BATCH_SIZE < MIN_BATCH_SIZE or MAX_BATCH_SIZE > 20:
        raise ValueError(f"Invalid batch size: MIN={MIN_BATCH_SIZE}, MAX={MAX_BATCH_SIZE}. Must be 1-20 with MIN <= MAX")
    if MIN_EMAIL_DELAY < 0 or MAX_EMAIL_DELAY < MIN_EMAIL_DELAY or MAX_EMAIL_DELAY > 60:
        raise ValueError(f"Invalid email delay: MIN={MIN_EMAIL_DELAY}, MAX={MAX_EMAIL_DELAY}. Must be 0-60 with MIN <= MAX")
    if MIN_BATCH_DELAY < 0 or MAX_BATCH_DELAY < MIN_BATCH_DELAY or MAX_BATCH_DELAY > 300:
        raise ValueError(f"Invalid batch delay: MIN={MIN_BATCH_DELAY}, MAX={MAX_BATCH_DELAY}. Must be 0-300 with MIN <= MAX")
except (ValueError, TypeError) as e:
    print(f"Error in rate limiting configuration: {e}")
    print("Using default values instead.")
    MIN_BATCH_SIZE = 3
    MAX_BATCH_SIZE = 7
    MIN_EMAIL_DELAY = 2.0
    MAX_EMAIL_DELAY = 12.0
    MIN_BATCH_DELAY = 30
    MAX_BATCH_DELAY = 90

# Sanitization limits
MAX_TEXT_LENGTH = 200
MAX_FILENAME_LENGTH = 100


def sanitize_text(text):
    """
    Sanitize text to prevent email header injection and limit abuse.
    
    - Removes newline and carriage return characters to prevent header injection
    - Limits text to 200 characters to prevent abuse
    - Strips whitespace
    """
    if not isinstance(text, str):
        return str(text)
    # Remove newlines and carriage returns to prevent header injection
    text = text.replace('\n', ' ').replace('\r', ' ')
    # Limit length to prevent abuse
    return text[:MAX_TEXT_LENGTH].strip()


def sanitize_filename(filename):
    """Sanitize filename for email attachment"""
    if not isinstance(filename, str):
        return "resume.pdf"
    # Remove path separators and special characters
    filename = os.path.basename(filename)
    # Only allow alphanumeric, dots, dashes, and underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename[:MAX_FILENAME_LENGTH] or "resume.pdf"


def validate_email(email):
    """
    Basic email validation using RFC 5322 simplified pattern.
    
    Returns True if email format is valid, False otherwise.
    """
    if not isinstance(email, str):
        return False
    email = email.strip()
    
    # Must contain @ symbol
    if '@' not in email:
        return False
    
    # Check for consecutive dots
    if '..' in email:
        return False
    
    # More strict regex pattern
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._+-]*[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    # Also allow single character local part
    local_part = email.split('@')[0]
    if len(local_part) == 1:
        pattern = r'^[a-zA-Z0-9]@[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def create_email_body(first_name, company):
    """Create personalized email body"""
    # Sanitize inputs to prevent injection
    first_name = sanitize_text(first_name)
    company = sanitize_text(company)
    
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
        df = pd.read_csv(RECIPIENTS_CSV)
        # Ensure the CSV has the required columns
        required_columns = ['first_name', 'company', 'email']
        if not all(col in df.columns for col in required_columns):
            print(f"Error: CSV must have columns: {', '.join(required_columns)}")
            return
        print(f"Loaded {len(df)} recipients from {RECIPIENTS_CSV}")
    except Exception as e:
        print(f"Error loading recipients: {e}")
        return
    
    # Load sent emails log
    if os.path.exists(SENT_LOG_FILE):
        try:
            sent_log_df = pd.read_csv(SENT_LOG_FILE)
            already_sent = set(sent_log_df['email'])
            print(f"Found {len(already_sent)} previously sent emails")
        except Exception as e:
            print(f"Warning: Could not read log file ({e}). Starting fresh.")
            already_sent = set()
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
        recipient_email = str(row['email']).strip()
        first_name = str(row['first_name'])
        company = str(row['company'])
        
        # Validate email format
        if not validate_email(recipient_email):
            print(f"[{index + 1}/{len(df)}] INVALID EMAIL: {recipient_email} - skipping")
            failed_count += 1
            continue
        
        if recipient_email in already_sent:
            print(f"[{index + 1}/{len(df)}] SKIPPED (already sent): {recipient_email}")
            skipped_count += 1
            continue
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = formataddr((SENDER_NAME, EMAIL_ADDRESS))
        msg['To'] = recipient_email
        # Sanitize company name to prevent header injection
        safe_company = sanitize_text(company)
        msg['Subject'] = f"Looking for Cloud Engineering / DevOps Opportunities at {safe_company}"
        
        # Set priority headers (if configured)
        if EMAIL_PRIORITY == "high":
            msg.add_header('X-Priority', '1')
            msg.add_header('X-MSMail-Priority', 'High')
            msg.add_header('Importance', 'High')
        
        # Add body
        body = create_email_body(first_name, company)
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        safe_filename = sanitize_filename(RESUME_FILENAME)
        part = MIMEApplication(resume_data, Name=safe_filename)
        part['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
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
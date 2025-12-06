# Bulk Recruiter Email Sender

This project is designed **for educational purposes only**. It demonstrates how to automate the process of sending personalized emails to multiple recruiters using Python. The goal is to help job seekers efficiently reach out to potential employers and improve their chances of getting noticed during the job search.

You can use either:
- **Jupyter Notebook** (`Cold Mail Send.ipynb`) - Interactive notebook interface
- **Python Script** (`cold_mail_sender.py`) - Command-line interface with `.env` support

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

### Main Files
- `Cold Mail Send.ipynb` – Jupyter notebook to run the email automation interactively.
- `cold_mail_sender.py` – Python script for command-line execution with environment variable support.

### Configuration Files
- `.env.example` – Template for environment variables (copy to `.env` and fill in your details).
- `recipients_template.csv` – Template for recipient details (copy to `recipients.csv` and add your data).
- `requirements.txt` – Python dependencies.

### Data Files (Auto-generated/User-provided)
- `recipients.csv` – Input file with recipient details (`first_name`, `company`, `email`).
- `your_resume.pdf` – Your resume file to be attached (name it as you prefer).
- `sent_emails_log.csv` – Auto-generated log of sent emails to avoid duplicates.

## Disclaimer

> This tool is intended **solely for educational purposes** to understand Python-based email automation. The author does **not endorse or condone spamming or misuse** of this tool. Use responsibly and adhere to applicable laws and platform terms of service when sending emails.

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Your Settings

**Option A: Using .env file (Recommended for Python Script)**

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your details:
   - `EMAIL_ADDRESS` – Your Gmail address
   - `EMAIL_PASSWORD` – Your Gmail App Password ([How to create](https://medium.com/@varunprakashs/how-to-create-an-app-password-in-google-for-less-secure-apps-4828e67693cd))
   - `RESUME_PATH` – Path to your resume file
   - `SENDER_NAME` – Your full name
   - `LINKEDIN_URL` – Your LinkedIn profile URL

**Option B: Edit the Jupyter Notebook directly**

- Open `Cold Mail Send.ipynb` and update the constants in the code cell.

### 3. Prepare Recipients List

1. Copy the template:
   ```bash
   cp recipients_template.csv recipients.csv
   ```

2. Edit `recipients.csv` with your recipient data (format: `first_name,company,email`):
   ```
   John,Amazon,john.recruiter@example.com
   Jane,Google,jane.recruiter@example.com
   ```

### 4. Add Your Resume

Place your resume PDF in the project directory and update the filename in your configuration.

### 5. Run the Tool

**Using Python Script:**
```bash
python cold_mail_sender.py
```

**Using Jupyter Notebook:**
Open `Cold Mail Send.ipynb` in Jupyter and run the cells.



## Recommended Platforms

- **Jupyter Notebook**: Anaconda, JupyterLab, Google Colab
- **Python Script**: Any Python 3.7+ environment, GitHub Codespaces, local machine
- **Cloud**: GitHub Codespaces, Anaconda Cloud

## Security Notes

⚠️ **Important**: Never commit sensitive files to version control!

The `.gitignore` file is configured to exclude:
- `.env` (your credentials)
- `recipients.csv` (recipient data)
- `sent_emails_log.csv` (logs)
- Resume files (`.pdf`, `.doc`, `.docx`)

Always keep your credentials and personal data secure.

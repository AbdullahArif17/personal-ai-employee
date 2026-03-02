# Quickstart Guide: Silver Tier Features

## Prerequisites
- Python 3.13+
- uv package manager
- Personal Gmail account with API access enabled
- Personal LinkedIn account with API access (if using official API)
- Valid GEMINI_API_KEY in .env file

## Setup

### 1. Install Dependencies
```bash
uv pip install google-api-python-client google-auth-oauthlib linkedin-api playwright
```

### 2. Configure API Credentials
Add the following to your `.env` file:
```bash
# Gmail API credentials
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token

# LinkedIn API credentials
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# WhatsApp automation (if needed)
WHATSAPP_USERNAME=your_whatsapp_username
WHATSAPP_PASSWORD=your_whatsapp_password
```

### 3. Initialize OAuth for Gmail
Run the Gmail OAuth setup script to authenticate and get your tokens:
```bash
python src/gmail_oauth_setup.py
```

## Running the Silver Tier Features

### 1. Start the Gmail Watcher
```bash
python src/gmail_watcher.py
```

### 2. Process Emails
When emails appear in the Needs_Action folder, process them:
```bash
python src/email_mcp.py
```

### 3. Generate LinkedIn Posts
To generate a new LinkedIn post:
```bash
python src/linkedin_poster.py
```

### 4. Monitor Approved Actions
The system automatically processes approved actions:
```bash
python src/approved_watcher.py
```

## Human-in-the-Loop Workflow

1. Gmail watcher puts new emails in `Needs_Action` folder
2. AI processes emails and puts drafts in `Pending_Approval` folder
3. User reviews and moves approved items to `Approved` folder
4. Approved watcher processes the actions and moves to `Done` folder
5. All actions are logged in the `Logs` folder

## Rate Limits
- Gmail: Max 10 emails processed per run
- LinkedIn: Max 3 posts per day
- These limits are enforced automatically by the system
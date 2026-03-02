# Gmail Setup for Personal AI Employee

This guide explains how to set up Gmail access for the Personal AI Employee system using IMAP and SMTP with App Passwords.

## Prerequisites

- A Gmail account
- Two-Factor Authentication enabled on your Gmail account

## Step-by-Step Setup

### 1. Enable Two-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security"
3. Under "Signing in to Google," select "2-Step Verification"
4. Follow the prompts to enable 2FA

### 2. Generate a Gmail App Password
1. Go back to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security"
3. Under "Signing in to Google," select "App passwords"
4. You may need to sign in again
5. Select "Mail" as the app and "Other (Custom name)" and enter a name like "AI Employee"
6. Click "Generate"
7. You'll receive a 16-character password (with spaces)

### 3. Configure Your Environment
1. Copy the 16-character app password
2. Add the following to your `.env` file:

```
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
```

Note: The app password may contain spaces - include them as shown.

### 4. Test the Connection
Run the Gmail watcher to test the connection:

```bash
python src/gmail_watcher.py
```

## Security Notes

- The App Password acts as an alternate password for your Gmail account
- It's limited to the specific app (in this case, your AI Employee)
- You can revoke the App Password anytime in your Google Account settings
- Never share your App Password or commit it to version control

## Troubleshooting

If you encounter authentication errors:
1. Verify that Two-Factor Authentication is enabled
2. Ensure the App Password is entered correctly (including spaces)
3. Check that your Gmail account allows "Less secure app access" (this is usually automatic with App Passwords)
4. Make sure you're using the App Password and not your regular Gmail password

## Alternative: OAuth 2.0

If you prefer OAuth 2.0 instead of App Passwords, you can set up Google Cloud Console credentials, but this requires a credit card for verification. The App Password method is simpler and doesn't require a credit card.
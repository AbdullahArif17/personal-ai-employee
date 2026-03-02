"""
Gmail authentication module for the Personal AI Employee system.
Handles IMAP authentication for Gmail access using app password.
"""
import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_gmail_imap_credentials() -> bool:
    """
    Validate Gmail IMAP credentials from environment variables.

    Returns:
        True if credentials are valid, False otherwise
    """
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')

    if not gmail_email or not gmail_app_password:
        print("Error: GMAIL_EMAIL and GMAIL_APP_PASSWORD not found in environment variables.")
        print("Please set these in your .env file using a Gmail app password.")
        return False

    # Basic validation of email format
    if "@" not in gmail_email or "." not in gmail_email:
        print("Error: Invalid email format for GMAIL_EMAIL.")
        return False

    # App passwords are typically 16 characters
    if len(gmail_app_password.replace(" ", "")) != 16:
        print("Warning: Gmail app password should be 16 characters (may include spaces)")

    return True


def get_gmail_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Get Gmail credentials from environment variables.

    Returns:
        Tuple of (email, app_password) if available, (None, None) otherwise
    """
    gmail_email = os.getenv('GMAIL_EMAIL')
    gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')

    if not gmail_email or not gmail_app_password:
        return (None, None)

    return (gmail_email, gmail_app_password)


if __name__ == '__main__':
    # Test the credentials
    valid = validate_gmail_imap_credentials()
    if valid:
        print("Gmail IMAP credentials are properly configured!")
    else:
        print("Gmail IMAP credentials are missing or invalid!")
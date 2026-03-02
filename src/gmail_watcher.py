"""
Gmail watcher for the Personal AI Employee system.
Monitors Gmail for unread emails using IMAP and saves them as .md files in Needs_Action folder.
"""
import email
import imaplib
import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GmailWatcher:
    """Gmail watcher implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "D:/giaic/personal-ai-employee/AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"

        # Get Gmail credentials from environment
        self.gmail_email = os.getenv('GMAIL_EMAIL')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')

        # Get dry run setting
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'

        if not self.gmail_email or not self.gmail_app_password:
            raise ValueError("GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in environment variables.")

        # Create directories if they don't exist
        self.needs_action_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def connect_to_imap(self) -> imaplib.IMAP4_SSL:
        """
        Connect to Gmail IMAP server.

        Returns:
            IMAP4_SSL connection object
        """
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)

        # Login using email and app password
        mail.login(self.gmail_email, self.gmail_app_password)

        # Select the inbox
        mail.select('inbox')

        return mail

    def check_unread_emails(self):
        """
        Check for unread emails in Gmail using IMAP.
        """
        mail = self.connect_to_imap()

        try:
            # Search for unread emails
            status, messages = mail.search(None, 'UNSEEN')

            if status != 'OK':
                print("Error searching for emails")
                return

            # Get email IDs
            email_ids = messages[0].split()

            if not email_ids:
                print("No unread emails found")
                return

            print(f"Found {len(email_ids)} unread emails")

            for email_id in email_ids:
                # Fetch the email
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                if status != 'OK':
                    continue

                # Parse the email
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Extract email data
                        sender = str(msg.get('From', 'Unknown'))
                        subject = str(msg.get('Subject', 'No Subject'))
                        date = str(msg.get('Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

                        # Extract body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True)
                                    if body:
                                        body = body.decode('utf-8', errors='ignore')
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')

                        # Create filename
                        # Clean sender and subject for filename
                        clean_sender = "".join(c for c in sender if c.isalnum() or c in (' ', '-', '_', '@', '.')).rstrip()
                        clean_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_', '@', '.')).rstrip()

                        # Limit length of filename parts
                        clean_sender = clean_sender[:50]  # Limit sender name
                        clean_subject = clean_subject[:50]  # Limit subject

                        # Format date for filename
                        filename_date = datetime.now().strftime('%Y%m%d_%H%M%S')

                        filename = f"EMAIL_{clean_sender}_{clean_subject}_{filename_date}.md"
                        filepath = self.needs_action_path / filename

                        # Handle filename conflicts
                        counter = 1
                        original_filepath = filepath
                        while filepath.exists():
                            filepath = self.needs_action_path / f"EMAIL_{clean_sender}_{clean_subject}_{filename_date}_{counter}.md"
                            counter += 1

                        # Prepare content
                        content = f"""# Gmail Message: {subject}

**From:** {sender}
**Date:** {date}

## Message Content
{body}

*Email imported from Gmail on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

                        # Save the email as markdown file (if not in dry run mode)
                        if self.dry_run:
                            print(f"(DRY_RUN) Would save email: {filepath.name}")
                            print(f"(DRY_RUN) Content preview: {content[:200]}...")
                        else:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)

                            print(f"Saved email: {filepath.name}")

                        # Log the action
                        self._log_action("EMAIL_SAVED", f"Saved email: {filepath.name}")

                        # Mark email as read
                        if not self.dry_run:
                            mail.store(email_id, '+FLAGS', '\\Seen')
                            print(f"Marked email as read: {email_id.decode()}")
                            self._log_action("EMAIL_MARKED_READ", f"Marked email as read: {email_id.decode()}")

        finally:
            # Logout from IMAP
            mail.logout()

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "dry_run": self.dry_run
        }

        # Create log filename based on today's date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        # Read existing log entries or initialize empty list
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write updated logs back to file
        if not self.dry_run:  # Only write logs if not in dry run mode
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)

    def run_continuous_monitoring(self, interval_minutes: int = 2):
        """
        Run continuous monitoring of Gmail.

        Args:
            interval_minutes: How often to check for new emails (in minutes)
        """
        print(f"Starting continuous Gmail monitoring (checking every {interval_minutes} minutes)")
        print(f"Dry run mode: {self.dry_run}")
        print("Press Ctrl+C to stop")

        try:
            while True:
                print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for unread emails...")
                self.check_unread_emails()
                print(f"Waiting {interval_minutes} minutes before next check...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\nStopping Gmail monitoring...")


def main():
    """Main function to run the Gmail watcher."""
    watcher = GmailWatcher()

    # Run continuous monitoring (checks every 2 minutes)
    watcher.run_continuous_monitoring(interval_minutes=2)


if __name__ == "__main__":
    main()
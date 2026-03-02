"""
Gmail watcher for the Personal AI Employee system.
Monitors Gmail for unread emails and saves them as .md files in Needs_Action folder.
"""
import base64
import json
import os
import time
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from google.auth.exceptions import RefreshError
    from googleapiclient.errors import HttpError
    from gmail_auth import get_authenticated_service
except ImportError as e:
    print(f"Error importing Gmail dependencies: {e}")
    print("Please install required packages: pip install google-api-python-client google-auth-oauthlib")


class GmailWatcher:
    """Gmail watcher implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.logs_path = self.vault_path / "Logs"

        # Rate limiting: max 10 emails processed per run
        self.max_emails_per_run = 10

        # Create directories if they don't exist
        self.needs_action_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def check_unread_emails(self) -> List[Dict]:
        """
        Check for unread emails in Gmail.

        Returns:
            List of email dictionaries with id, sender, subject, date, snippet
        """
        service = get_authenticated_service()
        if not service:
            print("Error: Could not authenticate with Gmail API")
            return []

        try:
            # Query for unread emails
            results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=self.max_emails_per_run
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()

                email_data = self._extract_email_data(msg)
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as error:
            print(f"An error occurred while fetching emails: {error}")
            return []
        except RefreshError as error:
            print(f"Token refresh error: {error}")
            return []

    def _extract_email_data(self, message: Dict) -> Optional[Dict]:
        """
        Extract relevant data from a Gmail message.

        Args:
            message: Raw Gmail message data

        Returns:
            Dictionary with extracted email data, or None if extraction fails
        """
        try:
            headers = message['payload']['headers']

            # Extract email components
            sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown')
            subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')

            # Get date
            date_header = next((header['value'] for header in headers if header['name'].lower() == 'date'), '')

            # Get body snippet
            body_snippet = message.get('snippet', '')[:500]  # First 500 chars

            # Get message ID
            message_id = message['id']

            # Determine importance (basic implementation)
            importance_level = self._determine_importance(sender, subject, body_snippet)

            return {
                'id': message_id,
                'sender': sender,
                'subject': subject,
                'date_received': date_header,
                'body_snippet': body_snippet,
                'status': 'needs_action',
                'importance_level': importance_level,
                'raw_data': message
            }
        except Exception as e:
            print(f"Error extracting email data: {e}")
            return None

    def _determine_importance(self, sender: str, subject: str, body: str) -> str:
        """
        Determine the importance level of an email.

        Args:
            sender: Email sender
            subject: Email subject
            body: Email body snippet

        Returns:
            Importance level ('critical', 'high', 'medium', 'low')
        """
        # Basic importance determination
        high_priority_keywords = ['urgent', 'asap', 'important', 'critical', 'emergency', 'deadline']
        medium_priority_keywords = ['meeting', 'review', 'request', 'follow', 'remind']

        combined_text = f"{sender} {subject} {body}".lower()

        for keyword in high_priority_keywords:
            if keyword in combined_text:
                return 'high'

        for keyword in medium_priority_keywords:
            if keyword in combined_text:
                return 'medium'

        return 'low'

    def save_emails_as_md_files(self, emails: List[Dict]) -> int:
        """
        Save emails as .md files in the Needs_Action folder.

        Args:
            emails: List of email dictionaries to save

        Returns:
            Number of emails successfully saved
        """
        saved_count = 0

        for email in emails:
            try:
                # Create filename based on subject and timestamp
                subject_clean = "".join(c for c in email['subject'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                if not subject_clean:
                    subject_clean = "untitled"

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"GMAIL_{timestamp}_{subject_clean}.md"
                filepath = self.needs_action_path / filename

                # Handle filename conflicts
                counter = 1
                original_filepath = filepath
                while filepath.exists():
                    filepath = self.needs_action_path / f"GMAIL_{timestamp}_{subject_clean}_{counter}.md"
                    counter += 1

                # Create markdown content
                md_content = f"""# Gmail Message: {email['subject']}

**From:** {email['sender']}
**Date:** {email['date_received']}
**Importance:** {email['importance_level'].title()}
**Message ID:** {email['id']}

## Preview
{email['body_snippet']}

## Raw Data
```
Status: {email['status']}
```

*Email imported from Gmail on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

                # Write the file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(md_content)

                saved_count += 1
                print(f"Saved email: {filepath.name}")

            except Exception as e:
                print(f"Error saving email {email.get('subject', 'Unknown')}: {e}")

        return saved_count

    def mark_emails_as_read(self, email_ids: List[str]) -> int:
        """
        Mark emails as read in Gmail.

        Args:
            email_ids: List of email IDs to mark as read

        Returns:
            Number of emails successfully marked as read
        """
        service = get_authenticated_service()
        if not service:
            print("Error: Could not authenticate with Gmail API")
            return 0

        marked_count = 0

        for email_id in email_ids:
            try:
                # Remove the UNREAD label
                service.users().messages().modify(
                    userId='me',
                    id=email_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

                marked_count += 1
                print(f"Marked email as read: {email_id}")

            except Exception as e:
                print(f"Error marking email {email_id} as read: {e}")

        return marked_count

    def process_unread_emails(self) -> Dict[str, int]:
        """
        Process all unread emails: fetch, save as MD files, mark as read.

        Returns:
            Dictionary with processing results
        """
        print("Checking for unread emails...")

        # Get unread emails
        emails = self.check_unread_emails()
        print(f"Found {len(emails)} unread emails")

        if not emails:
            return {'fetched': 0, 'saved': 0, 'marked_read': 0}

        # Save emails as markdown files
        saved_count = self.save_emails_as_md_files(emails)
        print(f"Saved {saved_count} emails as markdown files")

        # Extract email IDs to mark as read
        email_ids = [email['id'] for email in emails]

        # Mark emails as read
        marked_count = self.mark_emails_as_read(email_ids)
        print(f"Marked {marked_count} emails as read")

        # Log the action
        self._log_action("GMAIL_CHECK", f"Fetched {len(emails)} emails, saved {saved_count}, marked {marked_count} as read")

        return {
            'fetched': len(emails),
            'saved': saved_count,
            'marked_read': marked_count
        }

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "processor": "Gmail Watcher"
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
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """
        Run continuous monitoring of Gmail.

        Args:
            interval_minutes: How often to check for new emails (in minutes)
        """
        print(f"Starting continuous Gmail monitoring (checking every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")

        try:
            while True:
                self.process_unread_emails()
                print(f"Waiting {interval_minutes} minutes before next check...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            print("\nStopping Gmail monitoring...")


def main():
    """Main function to run the Gmail watcher."""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    watcher = GmailWatcher(vault_path)

    # Process any unread emails
    results = watcher.process_unread_emails()
    print(f"Processing complete: {results}")


if __name__ == "__main__":
    main()
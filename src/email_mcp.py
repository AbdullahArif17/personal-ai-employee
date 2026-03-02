"""
Email MCP (Mail Control Program) for the Personal AI Employee system.
Drafts email replies using Gemini AI and manages the approval workflow.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Note: Using SMTP instead of Gmail API, so no need for Gmail auth import


class EmailMCP:
    """Email MCP implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"

        # Rate limiting: max 10 emails processed per run
        self.max_emails_per_run = 10

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Create directories if they don't exist
        self.needs_action_path.mkdir(exist_ok=True)
        self.pending_approval_path.mkdir(exist_ok=True)
        self.approved_path.mkdir(exist_ok=True)
        self.done_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def process_email_for_reply(self, email_file_path: Path) -> Optional[str]:
        """
        Process an email file and generate a draft reply using Gemini AI.

        Args:
            email_file_path: Path to the email file to process

        Returns:
            Filename of the draft reply if successful, None otherwise
        """
        try:
            with open(email_file_path, 'r', encoding='utf-8') as f:
                email_content = f.read()

            # Extract the email details to generate a relevant reply
            reply_draft = self._generate_reply_draft(email_content)

            if not reply_draft:
                print(f"Could not generate reply for: {email_file_path.name}")
                return None

            # Save the draft reply to Pending_Approval folder
            draft_filename = self._save_reply_draft(reply_draft, email_file_path)
            return draft_filename

        except Exception as e:
            print(f"Error processing email {email_file_path.name} for reply: {e}")
            self._log_action("REPLY_GENERATION_ERROR", f"Error processing email {email_file_path.name}: {e}")
            return None

    def _generate_reply_draft(self, email_content: str) -> Optional[str]:
        """
        Generate a reply draft using Gemini AI based on the email content.

        Args:
            email_content: Content of the original email

        Returns:
            Generated reply draft if successful, None otherwise
        """
        prompt = f"""
Based on the following email, please generate a professional and appropriate reply:

{email_content}

Generate a draft reply that is:
- Professional and courteous
- Addresses the key points in the original email
- Appropriate for the context
- Concise but complete
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else None
        except Exception as e:
            print(f"Error generating reply draft with Gemini: {e}")
            return None

    def _save_reply_draft(self, reply_draft: str, original_email_path: Path) -> str:
        """
        Save the reply draft to the Pending_Approval folder.

        Args:
            reply_draft: The generated reply draft
            original_email_path: Path to the original email file

        Returns:
            Filename of the saved draft
        """
        # Create filename based on original email and timestamp
        original_name = original_email_path.stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"EMAIL_REPLY_{timestamp}_{original_name}.md"
        filepath = self.pending_approval_path / filename

        # Handle filename conflicts
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            filepath = self.pending_approval_path / f"EMAIL_REPLY_{timestamp}_{original_name}_{counter}.md"
            counter += 1

        # Create markdown content
        md_content = f"""# Email Reply Draft

## Original Email
{original_name}

## Reply Draft
{reply_draft}

## Details
- **Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Pending Approval
- **Original file**: {original_email_path.name}

## Action Required
Review this reply and move to Approved folder to send via email.
"""

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Saved email reply draft: {filepath.name}")

        # Log the action
        self._log_action("REPLY_DRAFT_CREATED", f"Created email reply draft: {filepath.name}")

        return filepath.name

    def send_approved_email(self, draft_file_path: Path) -> bool:
        """
        Send an approved email via Gmail API.

        Args:
            draft_file_path: Path to the approved email draft file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(draft_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract recipient, subject, and body from the draft
            recipient, subject, body = self._extract_email_details(content, draft_file_path)

            if not all([recipient, subject, body]):
                print(f"Could not extract email details from: {draft_file_path.name}")
                return False

            # Send the email via SMTP
            success = self._send_email_via_smtp(recipient, subject, body)

            if success:
                # Move the draft file to Done folder
                done_file_path = self.done_path / draft_file_path.name
                draft_file_path.rename(done_file_path)

                print(f"Email sent successfully: {recipient}")
                self._log_action("EMAIL_SENT", f"Sent email to {recipient}")
            else:
                print(f"Failed to send email: {recipient}")
                self._log_action("EMAIL_SEND_FAILED", f"Failed to send email to {recipient}")

            return success

        except Exception as e:
            print(f"Error sending approved email {draft_file_path.name}: {e}")
            self._log_action("EMAIL_SEND_ERROR", f"Error sending approved email {draft_file_path.name}: {e}")
            return False

    def _extract_email_details(self, content: str, original_file_path: Path) -> tuple:
        """
        Extract recipient, subject, and body from the draft content.
        This is a simplified implementation - in a real system, we'd have a more structured format.

        Args:
            content: Content of the draft file
            original_file_path: Path to the original email file

        Returns:
            Tuple of (recipient, subject, body) or (None, None, None) if extraction fails
        """
        # Try to determine recipient from the original email filename
        original_name = original_file_path.stem

        # Extract recipient from original email (simplified approach)
        # In a real system, this would be more sophisticated
        recipient = self._extract_recipient_from_original(original_file_path)

        if not recipient:
            # If we can't extract from original, try to determine from draft content
            lines = content.split('\n')
            for line in lines:
                if 'From:' in line:
                    # Extract email address
                    import re
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                    if email_match:
                        recipient = email_match.group()
                        break

        # For now, use a default subject based on original
        subject = f"Re: {original_name.replace('GMAIL_', '').replace('_', ' ')}"

        # Extract the actual reply content (between 'Reply Draft' and 'Details')
        lines = content.split('\n')
        reply_started = False
        reply_content = []

        for line in lines:
            if line.startswith('## Reply Draft'):
                reply_started = True
                continue
            elif line.startswith('## Details'):
                reply_started = False
                continue

            if reply_started:
                reply_content.append(line)

        body = '\n'.join(reply_content).strip()

        return recipient, subject, body

    def _extract_recipient_from_original(self, original_file_path: Path) -> Optional[str]:
        """
        Extract recipient from the original email file.
        This is a simplified implementation.

        Args:
            original_file_path: Path to the original email file

        Returns:
            Recipient email address if found, None otherwise
        """
        try:
            with open(original_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for sender in the original email content
            lines = content.split('\n')
            for line in lines:
                if line.startswith('**From:**'):
                    import re
                    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                    if email_match:
                        return email_match.group()
        except:
            pass

        return None

    def _send_email_via_smtp(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            True if successful, False otherwise
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        # Get Gmail credentials from environment
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')

        if not gmail_email or not gmail_app_password:
            print("Error: GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in environment variables.")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = gmail_email
            msg['To'] = to
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Use TLS port
            server.starttls()  # Enable security
            server.login(gmail_email, gmail_app_password)

            # Send email
            text = msg.as_string()
            server.sendmail(gmail_email, to, text)
            server.quit()

            print(f"Message sent successfully to: {to}")
            return True

        except Exception as e:
            print(f"Error sending email via SMTP: {e}")
            return False

    def process_all_pending_emails(self) -> int:
        """
        Process all emails in the Needs_Action folder to generate reply drafts.

        Returns:
            Number of emails processed
        """
        email_files = list(self.needs_action_path.glob("*.md")) + list(self.needs_action_path.glob("*.txt"))

        # Only process up to the max per run
        email_files = email_files[:self.max_emails_per_run]

        processed_count = 0

        for email_file in email_files:
            if email_file.name.startswith("GMAIL_"):  # Only process Gmail emails
                draft_filename = self.process_email_for_reply(email_file)
                if draft_filename:
                    processed_count += 1
                    print(f"Generated reply draft: {draft_filename}")

        return processed_count

    def check_and_send_approved_emails(self) -> int:
        """
        Check for approved emails in the Approved folder and send them.

        Returns:
            Number of emails sent
        """
        draft_files = list(self.approved_path.glob("EMAIL_REPLY_*.md"))

        sent_count = 0

        for draft_file in draft_files:
            success = self.send_approved_email(draft_file)
            if success:
                sent_count += 1

        return sent_count

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "processor": "Email MCP"
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


def main():
    """Main function to run the Email MCP."""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    mcp = EmailMCP(vault_path)

    # Process all pending emails to generate reply drafts
    processed_count = mcp.process_all_pending_emails()
    print(f"Processed {processed_count} emails for reply drafts")


if __name__ == "__main__":
    main()
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import json
import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Load environment variables
load_dotenv()


class EmailSender:
    """Handles sending emails via SMTP."""

    def __init__(self):
        self.gmail_email = os.getenv('GMAIL_EMAIL')
        self.gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')

        if not self.gmail_email or not self.gmail_app_password:
            raise ValueError("GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in environment variables.")

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email via SMTP.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Use TLS port
            server.starttls()  # Enable security
            server.login(self.gmail_email, self.gmail_app_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.gmail_email, to, text)
            server.quit()

            print(f"SUCCESS: Email sent successfully to: {to}")
        except Exception as e:
            print(f"ERROR: Error sending email to {to}: {e}")
            return False


class ApprovedFileHandler(FileSystemEventHandler):
    """Handles file system events in the Approved folder."""

    def __init__(self, vault_path: Path, dry_run: bool = False):
        super().__init__()
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.approved_path = vault_path / "Approved"
        self.done_path = vault_path / "Done"
        self.logs_path = vault_path / "Logs"

        # Create email sender instance
        self.email_sender = EmailSender()

    def on_created(self, event):
        """Handle file creation events in the Approved folder."""
        if event.is_directory:
            return

        # Only process .md files in the Approved folder
        if Path(event.src_path).suffix.lower() == '.md' and Path(event.src_path).parent == self.approved_path:
            print(f"INFO: New approved file detected: {Path(event.src_path).name}")
            self._process_approved_file(event.src_path)

    def on_moved(self, event):
        """Handle file move events in the Approved folder."""
        if event.is_directory:
            return

        # Only process .md files moved into the Approved folder
        if Path(event.dest_path).suffix.lower() == '.md' and Path(event.dest_path).parent == self.approved_path:
            print(f"INFO: Approved file moved: {Path(event.dest_path).name}")
            self._process_approved_file(event.dest_path)

    def _process_approved_file(self, file_path: str):
        """Process an approved file."""
        try:
            file_path_obj = Path(file_path)

            print(f"INFO: Processing approved file: {file_path_obj.name}")

            # Read the file content
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse the file to extract action and other fields
            action, to_email, subject, body = self._parse_approval_file(content)

            if not action:
                print(f"WARNING: No action specified in file: {file_path_obj.name}")
                self._log_action("ACTION_PARSE_ERROR", f"No action specified in file: {file_path_obj.name}")
                return

            # Execute the appropriate action
            if action == "send_email":
                self._execute_email_action(to_email, subject, body, file_path_obj)
            elif action == "post_tweet":
                self._execute_tweet_action(body, file_path_obj)
            else:
                print(f"WARNING: Unknown action '{action}' in file: {file_path_obj.name}")
                self._log_action("UNKNOWN_ACTION", f"Unknown action '{action}' in file: {file_path_obj.name}")

            # Move the file to Done folder after processing
            self._move_to_done(file_path_obj)

        except Exception as e:
            error_msg = f"Error processing approved file {file_path}: {str(e)}"
            print(f"ERROR: {error_msg}")
            self._log_action("PROCESSING_ERROR", error_msg)

    def _parse_approval_file(self, content: str) -> tuple:
        """
        Parse the approval file to extract action, to, subject, and body.

        Args:
            content: Full content of the approval file

        Returns:
            Tuple of (action, to_email, subject, body) or (None, None, None, content if no header)
        """
        lines = content.split('\n')

        # Look for YAML-style header between ---
        if len(lines) >= 3 and lines[0].strip() == '---':
            header_lines = []
            header_end_idx = -1

            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    header_end_idx = i
                    break
                else:
                    header_lines.append(line)

            if header_end_idx != -1:
                # Parse the header
                header_dict = {}
                for header_line in header_lines:
                    if ':' in header_line:
                        key, value = header_line.split(':', 1)
                        header_dict[key.strip().lower()] = value.strip()

                # Extract fields
                action = header_dict.get('action')
                to_email = header_dict.get('to')
                subject = header_dict.get('subject')

                # Extract the body (everything after the header)
                body_lines = lines[header_end_idx + 1:]
                body = '\n'.join(body_lines).strip()

                return action, to_email, subject, body

        # If no header found, return None for action and use full content as body
        return None, None, None, content

    def _execute_email_action(self, to_email: str, subject: str, body: str, file_path: Path):
        """Execute the send_email action."""
        if not to_email or not subject:
            print(f"WARNING: Missing email fields (to: {to_email}, subject: {subject}) in file: {file_path.name}")
            self._log_action("EMAIL_FIELDS_MISSING", f"Missing email fields in file: {file_path.name}")
            return

        print(f"EMAIL: Preparing to send email to: {to_email}")
        print(f"EMAIL: Subject: {subject}")

        if self.dry_run:
            print(f"(DRY RUN) Would send email to: {to_email}")
            self._log_action("EMAIL_DRY_RUN", f"Would send email to: {to_email}, subject: {subject}")
        else:
            success = self.email_sender.send_email(to_email, subject, body)
            if success:
                self._log_action("EMAIL_SENT", f"Email sent to: {to_email}, subject: {subject}")
            else:
                self._log_action("EMAIL_SEND_FAILED", f"Failed to send email to: {to_email}")

    def _move_to_done(self, file_path: Path):
        """Move the processed file to the Done folder."""
        if self.dry_run:
            print(f"(DRY RUN) Would move {file_path.name} to Done folder")
            return

        # Define destination file path
        dest_file = self.done_path / file_path.name

        # Handle filename conflicts by appending a number
        counter = 1
        original_dest_file = dest_file
        while dest_file.exists():
            stem = original_dest_file.stem
            suffix = original_dest_file.suffix
            dest_file = self.done_path / f"{stem}_{counter}{suffix}"
            counter += 1

        # Move the file
        file_path.rename(dest_file)

        print(f"SUCCESS: Moved file to Done: {dest_file.name}")
        self._log_action("FILE_MOVED_DONE", f"Moved file to Done: {dest_file.name}")

    def _execute_tweet_action(self, content: str, file_path: Path):
        """Execute a Twitter/X post action."""
        if not content:
            print(f"WARNING: Empty content for Twitter post in file: {file_path.name}")
            self._log_action("TWITTER_EMPTY_CONTENT", f"Empty content for Twitter post in file: {file_path.name}")
            return False

        if self.dry_run:
            print(f"(DRY RUN) Would post to Twitter: {content[:50]}...")
            self._log_action("TWITTER_DRY_RUN", f"Would post to Twitter: {file_path.name}")
            return True

        try:
            # Import Twitter libraries
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import tweepy
            from config import config

            # Get Twitter credentials
            consumer_key = config.twitter_consumer_key
            consumer_secret = config.twitter_consumer_secret
            user_access_token = config.twitter_user_access_token
            user_access_secret = config.twitter_user_access_secret
            bearer_token = config.twitter_bearer_token

            if not all([consumer_key, consumer_secret, user_access_token, user_access_secret, bearer_token]):
                error_msg = f"Missing required Twitter API credentials for posting: {file_path.name}"
                print(error_msg)
                self._log_action("TWITTER_CREDENTIALS_MISSING", error_msg)
                return False

            # Authenticate with Twitter API v2
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=user_access_token,
                access_token_secret=user_access_secret
            )

            # Validate content length (Twitter has 280 character limit)
            if len(content) > 280:
                content = content[:277] + "..."

            # Post the tweet
            response = client.create_tweet(text=content)

            if response.data and 'id' in response.data:
                tweet_id = response.data['id']
                success_msg = f"Successfully posted to Twitter with ID: {tweet_id} from file: {file_path.name}"
                print(success_msg)
                self._log_action("TWITTER_POSTED", success_msg)
                return True
            else:
                error_msg = f"Failed to post to Twitter: {file_path.name}, no ID returned"
                print(error_msg)
                self._log_action("TWITTER_FAILED", error_msg)
                return False

        except Exception as e:
            error_msg = f"Error executing Twitter action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("TWITTER_EXECUTION_ERROR", error_msg)
            return False

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "dry_run": self.dry_run
        }

        if self.dry_run:
            print(f"(DRY RUN) Would log: {log_entry}")
            return

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


class HITLWatcher:
    """HITL watcher implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "D:/giaic/personal-ai-employee/AI_Employee_Vault", dry_run: bool = False):
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run

        # Override with environment variable if set
        env_dry_run = os.getenv('DRY_RUN', '').lower()
        if env_dry_run in ['true', '1', 'yes']:
            self.dry_run = True
        elif env_dry_run in ['false', '0', 'no']:
            self.dry_run = False

        self.observer = Observer()
        self.handler = ApprovedFileHandler(self.vault_path, self.dry_run)

    def start(self):
        """Start the HITL watcher."""
        approved_path = self.vault_path / "Approved"

        if not approved_path.exists():
            raise FileNotFoundError(f"Approved folder does not exist: {approved_path}")

        # Schedule the event handler for the Approved directory
        self.observer.schedule(self.handler, str(approved_path), recursive=False)

        # Start the observer
        self.observer.start()

        status_msg = f"HITL watcher started, monitoring: {approved_path}"
        print(status_msg)
        self._log_action("WATCHER_STARTED", status_msg)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the HITL watcher."""
        self.observer.stop()
        self.observer.join()
        print("\nSTOPPING: HITL watcher stopped")
        self._log_action("WATCHER_STOPPED", "HITL watcher stopped")

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "dry_run": self.dry_run
        }

        logs_path = self.vault_path / "Logs"
        logs_path.mkdir(exist_ok=True)

        # Create log filename based on today's date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_path / f"{today}.json"

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
    """Main function to run the HITL watcher."""
    # Get configuration from environment or use defaults
    vault_path = os.getenv('VAULT_PATH', 'D:/giaic/personal-ai-employee/AI_Employee_Vault')
    dry_run_env = os.getenv('DRY_RUN', 'false').lower()
    dry_run = dry_run_env in ['true', '1', 'yes']

    print(f"STARTING: HITL Watcher")
    print(f"INFO: Vault Path: {vault_path}")
    print(f"INFO: Dry Run Mode: {dry_run}")
    print(f"INFO: Watching for approved files in: {Path(vault_path) / 'Approved'}")
    print("-" * 50)

    # Create the watcher instance
    watcher = HITLWatcher(vault_path, dry_run)

    # Start watching
    try:
        watcher.start()
    except KeyboardInterrupt:
        print("\nSTOPPING: HITL watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()
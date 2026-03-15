"""
Approved folder watcher for the Personal AI Employee system.
Monitors the Approved folder for approved files and executes the appropriate actions.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Add the current directory to the path to allow importing from the same package
sys.path.insert(0, os.path.dirname(__file__))
from base_watcher import BaseWatcher

# Load environment variables
load_dotenv()


class ApprovedFileHandler(FileSystemEventHandler):
    """Handles file system events in the Approved folder."""

    def __init__(self, vault_path: Path, dry_run: bool):
        super().__init__()
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.approved_path = vault_path / "Approved"
        self.done_path = vault_path / "Done"
        self.logs_path = vault_path / "Logs"

    def on_created(self, event):
        """Handle file creation events in the Approved folder."""
        if event.is_directory:
            return

        # Only process files in the Approved folder (not subfolders)
        if Path(event.src_path).parent == self.approved_path:
            self._process_approved_file(event.src_path)

    def on_moved(self, event):
        """Handle file move events in the Approved folder."""
        if event.is_directory:
            return

        # Only process files moved into the Approved folder
        if Path(event.dest_path).parent == self.approved_path:
            self._process_approved_file(event.dest_path)

    def _process_approved_file(self, file_path: str):
        """Process an approved file."""
        try:
            file_path_obj = Path(file_path)

            # Determine the action type based on file content or naming convention
            action_type = self._determine_action_type(file_path_obj)

            if action_type == "email":
                self._execute_email_action(file_path_obj)
            elif action_type == "linkedin_post":
                self._execute_linkedin_action(file_path_obj)
            elif action_type == "twitter_post":
                self._execute_twitter_action(file_path_obj)
            elif action_type == "facebook_post":
                self._execute_facebook_action(file_path_obj)
            elif action_type == "instagram_post":
                self._execute_instagram_action(file_path_obj)
            elif action_type == "odoo_invoice":
                self._execute_odoo_action(file_path_obj)
            else:
                self._log_action("UNKNOWN_ACTION", f"Unknown action type for file: {file_path_obj.name}")
                return

            # Move the file to Done folder after processing
            self._move_to_done(file_path_obj)

        except Exception as e:
            error_msg = f"Error processing approved file {file_path}: {str(e)}"
            self._log_action("ERROR", error_msg)
            print(error_msg)

    def _determine_action_type(self, file_path: Path) -> str:
        """Determine the action type based on file content or naming."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # Check content for indicators (Gold tier additions)
            if "email" in content or "reply" in content or "gmail" in content:
                return "email"
            elif "linkedin" in content or "post" in content or "connection" in content:
                return "linkedin_post"
            elif "twitter" in content or "tweet" in content:
                return "twitter_post"
            elif "facebook" in content or "fb_post" in content:
                return "facebook_post"
            elif "instagram" in content or "ig_post" in content or "insta_post" in content:
                return "instagram_post"
            elif "invoice" in content or "odoo" in content or "billing" in content:
                return "odoo_invoice"

            # Check filename (Gold tier additions)
            name = file_path.name.lower()
            if "email" in name or "reply" in name:
                return "email"
            elif "linkedin" in name or "post" in name:
                return "linkedin_post"
            elif "twitter" in name or "tweet" in name:
                return "twitter_post"
            elif "facebook" in name or "fb_" in name:
                return "facebook_post"
            elif "instagram" in name or "ig_" in name or "insta_" in name:
                return "instagram_post"
            elif "invoice" in name or "odoo" in name or "billing" in name:
                return "odoo_invoice"

        except Exception:
            pass

        # Default to email if uncertain
        return "email"

    def _extract_email_details(self, content: str) -> tuple:
        """
        Extract recipient, subject, and body from the email content.

        Args:
            content: Content of the email file

        Returns:
            Tuple of (recipient, subject, body) or (None, None, None) if extraction fails
        """
        import re

        # Extract recipient from the original email (look for sender in the original email file)
        lines = content.split('\n')
        recipient = None

        # Look for the original email header information
        for line in lines:
            if '**From:**' in line:
                # Extract email address from the original email
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                if email_match:
                    recipient = email_match.group()
                    break
            elif '## Original Email' in line:
                # Look for the original email file name and extract recipient from it
                # This is a simplified approach
                continue

        # Extract subject if it's in the content
        subject = "Re: Approved Reply"

        # Extract the body content (the actual reply)
        body_started = False
        body_content = []

        for line in lines:
            if '## Reply Draft' in line:
                body_started = True
                continue
            elif '## Details' in line:
                body_started = False
                continue
            elif '## Action Required' in line:
                break

            if body_started:
                body_content.append(line)

        body = '\n'.join(body_content).strip()

        if not body:
            # If we couldn't extract from the structured format, use the whole content
            body = content[:1000]  # First 1000 characters as fallback

        return recipient, subject, body

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
        from dotenv import load_dotenv
        import os

        load_dotenv()

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

    def _execute_email_action(self, file_path: Path):
        """Execute an approved email action."""
        if self.dry_run:
            print(f"(DRY RUN) Would send email based on: {file_path.name}")
            self._log_action("EMAIL_DRY_RUN", f"Would send email based on: {file_path.name}")
            return

        try:
            # Extract email details from the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract recipient, subject, and body from the content
            recipient, subject, body = self._extract_email_details(content)

            if not all([recipient, subject, body]):
                error_msg = f"Could not extract email details from: {file_path.name}"
                print(error_msg)
                self._log_action("EMAIL_SEND_FAILED", error_msg)
                return

            # Send the email via SMTP
            success = self._send_email_via_smtp(recipient, subject, body)

            if success:
                self._log_action("EMAIL_SENT", f"Sent email to {recipient} based on: {file_path.name}")
                print(f"Email sent to {recipient} based on: {file_path.name}")
            else:
                self._log_action("EMAIL_SEND_FAILED", f"Failed to send email based on: {file_path.name}")
                print(f"Failed to send email based on: {file_path.name}")

        except Exception as e:
            error_msg = f"Error executing email action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("EMAIL_EXECUTION_ERROR", error_msg)

    def _execute_linkedin_action(self, file_path: Path):
        """Execute an approved LinkedIn post action."""
        if self.dry_run:
            print(f"(DRY RUN) Would post to LinkedIn based on: {file_path.name}")
            self._log_action("LINKEDIN_DRY_RUN", f"Would post to LinkedIn based on: {file_path.name}")
            return

        # For the IMAP approach, we're not actually posting to LinkedIn via API
        # Instead, we're just noting that the post has been approved for manual posting
        self._log_action("LINKEDIN_APPROVED", f"LinkedIn post approved for manual posting: {file_path.name}")
        print(f"LinkedIn post approved for manual posting: {file_path.name}")

        # In a real implementation, we might save the post content to a separate file
        # or database to indicate it's ready for manual posting to LinkedIn

    def _execute_twitter_action(self, file_path: Path):
        """Execute an approved Twitter post action."""
        if self.dry_run:
            print(f"(DRY RUN) Would post to Twitter based on: {file_path.name}")
            self._log_action("TWITTER_DRY_RUN", f"Would post to Twitter based on: {file_path.name}")
            return

        try:
            # Read the content to post
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the actual post content (skip any metadata)
            lines = content.split('\n')
            post_content = ""
            for line in lines:
                if not line.startswith('#') and not line.startswith('**') and line.strip():
                    post_content += line + "\n"

            post_content = post_content.strip()

            # Validate content length (Twitter has 280 character limit)
            if len(post_content) > 280:
                post_content = post_content[:277] + "..."

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
            # Also need bearer token for API v2
            bearer_token = config.twitter_bearer_token

            if not all([consumer_key, consumer_secret, user_access_token, user_access_secret, bearer_token]):
                error_msg = f"Missing Twitter API credentials for posting: {file_path.name}"
                print(error_msg)
                self._log_action("TWITTER_POST_FAILED", error_msg)
                return

            # Authenticate with Twitter API
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=user_access_token,
                access_token_secret=user_access_secret
            )

            # Post the tweet
            response = client.create_tweet(text=post_content)

            if response.data and 'id' in response.data:
                success_msg = f"Successfully posted to Twitter: {file_path.name}"
                print(success_msg)
                self._log_action("TWITTER_POSTED", success_msg)
            else:
                error_msg = f"Failed to post to Twitter: {file_path.name}"
                print(error_msg)
                self._log_action("TWITTER_POST_FAILED", error_msg)

        except Exception as e:
            error_msg = f"Error executing Twitter action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("TWITTER_EXECUTION_ERROR", error_msg)

    def _execute_facebook_action(self, file_path: Path):
        """Execute an approved Facebook post action."""
        if self.dry_run:
            print(f"(DRY RUN) Would post to Facebook based on: {file_path.name}")
            self._log_action("FACEBOOK_DRY_RUN", f"Would post to Facebook based on: {file_path.name}")
            return

        try:
            # Read the content to post
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the actual post content (skip any metadata)
            lines = content.split('\n')
            post_content = ""
            for line in lines:
                if not line.startswith('#') and not line.startswith('**') and line.strip():
                    post_content += line + "\n"

            post_content = post_content.strip()

            # Import Facebook libraries
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import requests
            from config import config

            # Get Facebook credentials
            access_token = config.facebook_access_token
            page_id = config.facebook_page_id

            if not all([access_token, page_id]):
                error_msg = f"Missing Facebook API credentials for posting: {file_path.name}"
                print(error_msg)
                self._log_action("FACEBOOK_POST_FAILED", error_msg)
                return

            # Prepare the post data
            post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            params = {
                'message': post_content,
                'access_token': access_token
            }

            # Make the POST request
            response = requests.post(post_url, params=params)

            if response.status_code == 200:
                response_data = response.json()
                post_id = response_data.get('id', 'unknown')
                success_msg = f"Successfully posted to Facebook (ID: {post_id}): {file_path.name}"
                print(success_msg)
                self._log_action("FACEBOOK_POSTED", success_msg)
            else:
                error_msg = f"Failed to post to Facebook: {file_path.name}, Error: {response.text}"
                print(error_msg)
                self._log_action("FACEBOOK_POST_FAILED", error_msg)

        except Exception as e:
            error_msg = f"Error executing Facebook action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("FACEBOOK_EXECUTION_ERROR", error_msg)

    def _execute_instagram_action(self, file_path: Path):
        """Execute an approved Instagram post action."""
        if self.dry_run:
            print(f"(DRY RUN) Would post to Instagram based on: {file_path.name}")
            self._log_action("INSTAGRAM_DRY_RUN", f"Would post to Instagram based on: {file_path.name}")
            return

        try:
            # Read the content to post
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract the actual post content (skip any metadata)
            lines = content.split('\n')
            post_content = ""
            for line in lines:
                if not line.startswith('#') and not line.startswith('**') and line.strip():
                    post_content += line + "\n"

            post_content = post_content.strip()

            # Import Instagram libraries
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import requests
            from config import config

            # Get Instagram credentials
            access_token = config.instagram_access_token
            account_id = config.instagram_account_id

            if not all([access_token, account_id]):
                error_msg = f"Missing Instagram API credentials for posting: {file_path.name}"
                print(error_msg)
                self._log_action("INSTAGRAM_POST_FAILED", error_msg)
                return

            # Create the media object
            creation_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            creation_params = {
                'caption': post_content,
                'access_token': access_token
            }

            # For text-only posts, we can't use Instagram's media upload directly
            # This is a simplified approach - real implementation would need image/media handling
            response = requests.post(creation_url, params=creation_params)

            if response.status_code == 200:
                response_data = response.json()
                container_id = response_data.get('id', '')

                # Publish the media
                publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
                publish_params = {
                    'creation_id': container_id,
                    'access_token': access_token
                }

                publish_response = requests.post(publish_url, params=publish_params)

                if publish_response.status_code == 200:
                    publish_data = publish_response.json()
                    post_id = publish_data.get('id', 'unknown')
                    success_msg = f"Successfully posted to Instagram (ID: {post_id}): {file_path.name}"
                    print(success_msg)
                    self._log_action("INSTAGRAM_POSTED", success_msg)
                else:
                    error_msg = f"Failed to publish Instagram post: {file_path.name}, Error: {publish_response.text}"
                    print(error_msg)
                    self._log_action("INSTAGRAM_PUBLISH_FAILED", error_msg)
            else:
                error_msg = f"Failed to create Instagram media: {file_path.name}, Error: {response.text}"
                print(error_msg)
                self._log_action("INSTAGRAM_CREATION_FAILED", error_msg)

        except Exception as e:
            error_msg = f"Error executing Instagram action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("INSTAGRAM_EXECUTION_ERROR", error_msg)

    def _execute_odoo_action(self, file_path: Path):
        """Execute an approved Odoo invoice creation action."""
        if self.dry_run:
            print(f"(DRY RUN) Would create invoice in Odoo based on: {file_path.name}")
            self._log_action("ODOO_DRY_RUN", f"Would create invoice in Odoo based on: {file_path.name}")
            return

        try:
            # Read the content to process
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Import Odoo libraries
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from odoo_rpc import ODOO
            from config import config

            # Get Odoo credentials
            url = config.odoo_url
            db = config.odoo_db
            username = config.odoo_username
            password = config.odoo_password

            if not all([url, db, username, password]):
                error_msg = f"Missing Odoo API credentials for invoice creation: {file_path.name}"
                print(error_msg)
                self._log_action("ODOO_INVOICE_FAILED", error_msg)
                return

            # Connect to Odoo
            odoo = ODOO(url, port=80, database=db, user=username, password=password)

            # Extract invoice details from content (simplified approach)
            # In a real implementation, we'd parse the content more thoroughly
            lines = content.split('\n')
            partner_name = "Default Customer"  # Would extract from content in real impl
            product_name = "Service"  # Would extract from content in real impl
            quantity = 1  # Would extract from content in real impl
            price_unit = 100.0  # Would extract from content in real impl

            # Search for partner
            partner_ids = odoo.res_partner.search([('name', '=', partner_name)])
            if not partner_ids:
                # Create partner if not found
                partner_id = odoo.res_partner.create({
                    'name': partner_name,
                    'customer_rank': 1  # Mark as customer
                })
            else:
                partner_id = partner_ids[0]

            # Search for product
            product_ids = odoo.product_product.search([('name', '=', product_name)])
            if not product_ids:
                # Create product if not found
                product_id = odoo.product_product.create({
                    'name': product_name,
                    'type': 'service',  # Use 'service' for services
                    'list_price': price_unit
                })
            else:
                product_id = product_ids[0]

            # Create invoice
            invoice_id = odoo.account_move.create({
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # 'out_invoice' for customer invoices
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_id,
                    'name': product_name,
                    'quantity': quantity,
                    'price_unit': price_unit,
                })]
            })

            # Validate and post the invoice
            odoo.account_move.action_post([invoice_id])

            success_msg = f"Successfully created invoice in Odoo (ID: {invoice_id}): {file_path.name}"
            print(success_msg)
            self._log_action("ODOO_INVOICE_CREATED", success_msg)

        except Exception as e:
            error_msg = f"Error executing Odoo action from {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("ODOO_EXECUTION_ERROR", error_msg)

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

        self._log_action("FILE_MOVED", f"Moved {file_path.name} to Done folder")

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

        # Create logs directory if it doesn't exist
        self.logs_path.mkdir(exist_ok=True)

        # Write updated logs back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)


class ApprovedWatcher(BaseWatcher):
    """Approved folder watcher implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault", dry_run: bool = True):
        super().__init__(vault_path, dry_run)

        # Override with environment variable if set
        env_dry_run = os.getenv('DRY_RUN', '').lower()
        if env_dry_run in ['true', '1', 'yes']:
            self.dry_run = True
        elif env_dry_run in ['false', '0', 'no']:
            self.dry_run = False

        self.observer = Observer()
        self.handler = ApprovedFileHandler(self.vault_path, self.dry_run)

    def start(self):
        """Start the approved folder watcher."""
        approved_path = self.vault_path / "Approved"

        if not approved_path.exists():
            raise FileNotFoundError(f"Approved folder does not exist: {approved_path}")

        # Schedule the event handler for the Approved directory
        self.observer.schedule(self.handler, str(approved_path), recursive=False)

        # Start the observer
        self.observer.start()

        status_msg = f"Approved folder watcher started, monitoring: {approved_path}"
        self.log_action("WATCHER_STARTED", status_msg)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the approved folder watcher."""
        self.observer.stop()
        self.observer.join()
        self.log_action("WATCHER_STOPPED", "Approved folder watcher stopped")


def main():
    """Main function to run the approved folder watcher."""
    # Get configuration from environment or use defaults
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the watcher instance
    watcher = ApprovedWatcher(vault_path)

    # Start watching
    try:
        watcher.start()
    except KeyboardInterrupt:
        print("\nStopping approved watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()
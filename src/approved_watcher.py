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

            # Check content for indicators
            if "email" in content or "reply" in content or "gmail" in content:
                return "email"
            elif "linkedin" in content or "post" in content or "connection" in content:
                return "linkedin_post"

            # Check filename
            name = file_path.name.lower()
            if "email" in name or "reply" in name:
                return "email"
            elif "linkedin" in name or "post" in name:
                return "linkedin_post"

        except Exception:
            pass

        # Default to email if uncertain
        return "email"

    def _execute_email_action(self, file_path: Path):
        """Execute an approved email action."""
        if self.dry_run:
            print(f"(DRY RUN) Would send email based on: {file_path.name}")
            self._log_action("EMAIL_DRY_RUN", f"Would send email based on: {file_path.name}")
            return

        # In a real implementation, this would send the email via Gmail API
        # For now, just log the action
        self._log_action("EMAIL_SENT", f"Sent email based on: {file_path.name}")
        print(f"Email sent based on: {file_path.name}")

    def _execute_linkedin_action(self, file_path: Path):
        """Execute an approved LinkedIn post action."""
        if self.dry_run:
            print(f"(DRY RUN) Would post to LinkedIn based on: {file_path.name}")
            self._log_action("LINKEDIN_DRY_RUN", f"Would post to LinkedIn based on: {file_path.name}")
            return

        # In a real implementation, this would post to LinkedIn via LinkedIn API
        # For now, just log the action
        self._log_action("LINKEDIN_POSTED", f"Posted to LinkedIn: {file_path.name}")
        print(f"Posted to LinkedIn: {file_path.name}")

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
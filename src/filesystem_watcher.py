"""
Filesystem watcher for the Personal AI Employee system.
Monitors the Inbox folder and copies new files to Needs_Action with metadata.
"""

import json
import os
import shutil
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


class InboxHandler(FileSystemEventHandler):
    """Handles file system events in the Inbox folder."""

    def __init__(self, vault_path: Path, dry_run: bool):
        super().__init__()
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.inbox_path = vault_path / "Inbox"
        self.needs_action_path = vault_path / "Needs_Action"
        self.logs_path = vault_path / "Logs"

    def on_created(self, event):
        """Handle file creation events in the Inbox folder."""
        if event.is_directory:
            return

        # Only process files in the Inbox folder (not subfolders)
        if Path(event.src_path).parent == self.inbox_path:
            self._process_new_file(event.src_path)

    def on_moved(self, event):
        """Handle file move events in the Inbox folder."""
        if event.is_directory:
            return

        # Only process files moved into the Inbox folder
        if Path(event.dest_path).parent == self.inbox_path:
            self._process_new_file(event.dest_path)

    def _process_new_file(self, file_path: str):
        """Process a new file in the Inbox folder."""
        try:
            file_path_obj = Path(file_path)

            # Create metadata for the file
            metadata = {
                "original_path": str(file_path_obj),
                "copied_at": datetime.now().isoformat(),
                "status": "new",
                "processed": False,
                "attempts": 0
            }

            # Copy file to Needs_Action folder with metadata sidecar
            self._copy_file_with_metadata(file_path_obj, metadata)

            # Log the action
            self._log_action("FILE_COPIED", f"Copied {file_path_obj.name} to Needs_Action")

        except Exception as e:
            error_msg = f"Error processing file {file_path}: {str(e)}"
            self._log_action("ERROR", error_msg)
            print(error_msg)

    def _copy_file_with_metadata(self, source_file: Path, metadata: Dict[str, Any]):
        """Copy file to Needs_Action folder and create metadata sidecar file."""
        if self.dry_run:
            print(f"(DRY RUN) Would copy {source_file.name} to Needs_Action with metadata")
            return

        # Define destination file path
        dest_file = self.needs_action_path / source_file.name

        # Handle filename conflicts by appending a number
        counter = 1
        original_dest_file = dest_file
        while dest_file.exists():
            stem = original_dest_file.stem
            suffix = original_dest_file.suffix
            dest_file = self.needs_action_path / f"{stem}_{counter}{suffix}"
            counter += 1

        # Copy the file
        shutil.copy2(source_file, dest_file)

        # Create metadata sidecar file
        metadata_file = self.needs_action_path / f"{dest_file.stem}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

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


class FilesystemWatcher(BaseWatcher):
    """Filesystem watcher implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault", dry_run: bool = True):
        super().__init__(vault_path, dry_run)

        # Override with environment variable if set
        env_dry_run = os.getenv('DRY_RUN', '').lower()
        if env_dry_run in ['true', '1', 'yes']:
            self.dry_run = True
        elif env_dry_run in ['false', '0', 'no']:
            self.dry_run = False

        self.observer = Observer()
        self.handler = InboxHandler(self.vault_path, self.dry_run)

    def start(self):
        """Start the filesystem watcher."""
        inbox_path = self.vault_path / "Inbox"

        if not inbox_path.exists():
            raise FileNotFoundError(f"Inbox folder does not exist: {inbox_path}")

        # Schedule the event handler for the Inbox directory
        self.observer.schedule(self.handler, str(inbox_path), recursive=False)

        # Start the observer
        self.observer.start()

        status_msg = f"Filesystem watcher started, monitoring: {inbox_path}"
        self.log_action("WATCHER_STARTED", status_msg)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the filesystem watcher."""
        self.observer.stop()
        self.observer.join()
        self.log_action("WATCHER_STOPPED", "Filesystem watcher stopped")


def main():
    """Main function to run the filesystem watcher."""
    # Get configuration from environment or use defaults
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the watcher instance
    watcher = FilesystemWatcher(vault_path)

    # Start watching
    try:
        watcher.start()
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        watcher.stop()


if __name__ == "__main__":
    main()
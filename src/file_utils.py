'''
File utilities for vault folder monitoring and state management in the Personal AI Employee system.
'''

import os
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    from .logger import setup_logger
except ImportError:
    # Fallback for when running as a script directly
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from logger import setup_logger

logger = setup_logger('file_utils')

class FileUtils:
    """
    Utilities for vault folder monitoring and state management.
    Provides functions for file operations, state tracking, and monitoring.
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize file utilities.

        Args:
            vault_path: Path to the vault (defaults to VAULT_PATH env var or './AI_Employee_Vault')
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))

        # Ensure vault structure exists
        self.ensure_vault_structure()

    def ensure_vault_structure(self):
        """Ensure the vault directory structure exists."""
        folders = [
            'Inbox',
            'Needs_Action',
            'Done',
            'Logs',
            'Pending_Approval',
            'Approved',
            'skills'
        ]

        for folder in folders:
            (self.vault_path / folder).mkdir(parents=True, exist_ok=True)

        logger.info(f"Vault structure ensured at {self.vault_path}")

    def get_files_in_folder(self, folder_name: str) -> List[Path]:
        """
        Get all files in a specified vault folder.

        Args:
            folder_name: Name of the folder (e.g., 'Needs_Action', 'Pending_Approval')

        Returns:
            List of file paths in the folder
        """
        folder_path = self.vault_path / folder_name
        if not folder_path.exists():
            logger.warning(f"Folder {folder_path} does not exist")
            return []

        files = []
        for item in folder_path.iterdir():
            if item.is_file():
                files.append(item)

        logger.debug(f"Found {len(files)} files in {folder_name}")
        return files

    def move_file(self, source: Path, destination_folder: str) -> bool:
        """
        Move a file from source to destination folder.

        Args:
            source: Source file path
            destination_folder: Destination folder name

        Returns:
            True if successful, False otherwise
        """
        try:
            dest_path = self.vault_path / destination_folder / source.name
            source.rename(dest_path)
            logger.info(f"Moved {source.name} to {destination_folder}")
            return True
        except Exception as e:
            logger.error(f"Error moving file {source.name}: {str(e)}")
            return False

    def read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read content from a file.

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string, or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Read {len(content)} characters from {file_path.name}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {file_path.name}: {str(e)}")
            return None

    def write_file_content(self, file_path: Path, content: str) -> bool:
        """
        Write content to a file.

        Args:
            file_path: Path to the file to write
            content: Content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.debug(f"Wrote {len(content)} characters to {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Error writing to file {file_path.name}: {str(e)}")
            return False

    def create_draft_file(self, content: str, folder: str, prefix: str = "draft") -> Optional[Path]:
        """
        Create a draft file with timestamp in the specified folder.

        Args:
            content: Content for the draft
            folder: Folder name to save the draft in
            prefix: Prefix for the filename

        Returns:
            Path to the created file, or None if error
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.txt"
            file_path = self.vault_path / folder / filename

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Created draft file: {filename}")
            return file_path
        except Exception as e:
            logger.error(f"Error creating draft file: {str(e)}")
            return None

    def is_file_older_than_days(self, file_path: Path, days: int) -> bool:
        """
        Check if a file is older than the specified number of days.

        Args:
            file_path: Path to the file
            days: Number of days

        Returns:
            True if file is older than specified days, False otherwise
        """
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            cutoff_time = datetime.now() - timedelta(days=days)
            return file_time < cutoff_time
        except Exception as e:
            logger.error(f"Error checking file age for {file_path.name}: {str(e)}")
            return False

    @property
    def pending_approval_path(self) -> Path:
        """
        Get the path to the Pending_Approval folder.

        Returns:
            Path object to the Pending_Approval folder
        """
        return self.vault_path / "Pending_Approval"

    def get_company_handbook_content(self) -> Optional[str]:
        """
        Get content from the Company Handbook.

        Returns:
            Company handbook content as string, or None if error
        """
        handbook_path = self.vault_path / "Company_Handbook.md"
        if handbook_path.exists():
            return self.read_file_content(handbook_path)
        else:
            logger.warning("Company handbook not found")
            return None

    def cleanup_old_pending_approvals(self, days: int) -> int:
        """
        Remove pending approval files older than specified days.

        Args:
            days: Number of days after which to remove files

        Returns:
            Number of files removed
        """
        pending_approval_path = self.vault_path / "Pending_Approval"
        if not pending_approval_path.exists():
            return 0

        files_to_remove = []
        for file_path in pending_approval_path.iterdir():
            if file_path.is_file() and self.is_file_older_than_days(file_path, days):
                files_to_remove.append(file_path)

        removed_count = 0
        for file_path in files_to_remove:
            try:
                file_path.unlink()
                logger.info(f"Removed old pending approval file: {file_path.name}")
                removed_count += 1
            except Exception as e:
                logger.error(f"Error removing old file {file_path.name}: {str(e)}")

        return removed_count


# Global file utilities instance
file_utils = FileUtils()


def get_file_utils() -> FileUtils:
    """Get the global file utilities instance."""
    return file_utils
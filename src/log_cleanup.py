'''
Log retention and cleanup functionality for the Personal AI Employee system.
Implements 90-day log retention policy and cleanup functionality.
'''

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from .logger import setup_logger

logger = setup_logger('log_cleanup')

def cleanup_old_logs(retention_days: int = 90) -> int:
    """
    Clean up log files older than the specified retention period.

    Args:
        retention_days: Number of days to retain logs (default: 90)

    Returns:
        Number of files removed
    """
    vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
    logs_path = vault_path / "Logs"

    if not logs_path.exists():
        logger.info(f"Logs directory does not exist: {logs_path}")
        return 0

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    removed_count = 0

    # Find log files that match date patterns (YYYY-MM-DD)
    for file_path in logs_path.iterdir():
        if file_path.is_file():
            # Extract date from filename (assuming format like YYYY-MM-DD.log)
            match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
            if match:
                try:
                    file_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                    if file_date < cutoff_date:
                        file_path.unlink()
                        logger.info(f"Removed old log file: {file_path.name}")
                        removed_count += 1
                except ValueError:
                    # If date parsing fails, skip the file
                    continue

    logger.info(f"Log cleanup completed: removed {removed_count} files")
    return removed_count

def auto_reject_old_pending_approvals(days: int = 30) -> int:
    """
    Auto-reject pending approval items that are older than specified days.

    Args:
        days: Number of days after which to auto-reject items (default: 30)

    Returns:
        Number of items auto-rejected
    """
    vault_path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
    pending_approval_path = vault_path / "Pending_Approval"

    if not pending_approval_path.exists():
        logger.info(f"Pending_Approval directory does not exist: {pending_approval_path}")
        return 0

    cutoff_date = datetime.now() - timedelta(days=days)
    rejected_count = 0

    for file_path in pending_approval_path.iterdir():
        if file_path.is_file():
            try:
                # Get file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

                if mod_time < cutoff_date:
                    # Move to Done folder with rejection note
                    rejection_note = f"REJECTED: Auto-rejected after {days} days in Pending_Approval\n\n"

                    # Read original content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()

                    # Write rejection note + original content to Done folder
                    done_path = vault_path / "Done" / f"REJECTED_{file_path.name}"
                    with open(done_path, 'w', encoding='utf-8') as f:
                        f.write(rejection_note + original_content)

                    # Remove original pending approval file
                    file_path.unlink()

                    logger.info(f"Auto-rejected pending approval item: {file_path.name}")
                    rejected_count += 1

            except Exception as e:
                logger.error(f"Error auto-rejecting {file_path.name}: {str(e)}")

    logger.info(f"Auto-rejection completed: {rejected_count} items rejected")
    return rejected_count

def run_cleanup_tasks():
    """
    Run all cleanup tasks: log retention and auto-rejection of old pending items.
    """
    logger.info("Starting cleanup tasks...")

    # Clean up old logs
    logs_removed = cleanup_old_logs()

    # Auto-reject old pending approvals
    items_rejected = auto_reject_old_pending_approvals()

    logger.info(f"Cleanup tasks completed: {logs_removed} logs removed, {items_rejected} items rejected")

if __name__ == "__main__":
    run_cleanup_tasks()
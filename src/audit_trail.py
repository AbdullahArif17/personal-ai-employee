'''
Comprehensive audit trail logging for the Personal AI Employee system.
Ensures all actions are logged for compliance and accountability.
'''

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger

logger = setup_logger('audit_trail')

class AuditTrailLogger:
    """
    Comprehensive audit trail logger for all Gold tier features.
    Ensures all actions are logged for compliance and accountability.
    """

    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize the audit trail logger.

        Args:
            vault_path: Path to the vault (uses VAULT_PATH env var if not provided)
        """
        self.vault_path = Path(vault_path or os.getenv('VAULT_PATH', './AI_Employee_Vault'))
        self.logs_path = self.vault_path / 'Logs'

        # Ensure logs directory exists
        self.logs_path.mkdir(parents=True, exist_ok=True)

    def log_action(self, action_type: str, component: str, success: bool, details: Dict[str, Any] = None,
                   user: str = "system", ip_address: str = "localhost"):
        """
        Log an action for audit trail compliance.

        Args:
            action_type: Type of action being logged (e.g., 'task_processing', 'social_media_post', 'invoice_creation')
            component: Component performing the action (e.g., 'ralph_loop', 'twitter_poster', 'odoo_integration')
            success: Whether the action was successful
            details: Additional details about the action
            user: User responsible for the action (default: 'system')
            ip_address: IP address of the user (default: 'localhost')
        """
        timestamp = datetime.now().isoformat()

        log_entry = {
            'timestamp': timestamp,
            'action_type': action_type,
            'component': component,
            'success': success,
            'user': user,
            'ip_address': ip_address,
            'details': details or {}
        }

        # Add to component-specific log
        component_log_path = self.logs_path / f"{component}_audit.json"
        self._append_to_log(component_log_path, log_entry)

        # Add to main audit log
        main_log_path = self.logs_path / "audit_trail.json"
        self._append_to_log(main_log_path, log_entry)

        # Log to standard logger as well
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUDIT TRAIL - {action_type} - {component} - {status}")

    def _append_to_log(self, log_path: Path, log_entry: Dict[str, Any]):
        """
        Append a log entry to the specified log file.

        Args:
            log_path: Path to the log file
            log_entry: Log entry to append
        """
        try:
            # Read existing logs if file exists
            if log_path.exists():
                with open(log_path, 'r', encoding='utf-8') as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back to file
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            logger.error(f"Error writing to audit log {log_path}: {e}")

    def log_task_processing(self, task_id: str, iteration: int, status: str, result: str = None):
        """
        Log task processing event for Ralph Wiggum Loop.

        Args:
            task_id: Unique identifier for the task
            iteration: Current iteration number
            status: Processing status ('started', 'retry', 'completed', 'failed')
            result: Result of the processing (if applicable)
        """
        details = {
            'task_id': task_id,
            'iteration': iteration,
            'status': status,
            'component': 'ralph_loop'
        }

        if result:
            details['result_length'] = len(result)

        self.log_action(
            action_type='task_processing',
            component='ralph_loop',
            success=(status != 'failed'),
            details=details
        )

    def log_social_media_action(self, action_type: str, platform: str, success: bool, details: Dict[str, Any] = None):
        """
        Log social media actions (Twitter, Facebook, Instagram).

        Args:
            action_type: Type of social media action (e.g., 'tweet_posted', 'facebook_posted', 'instagram_posted')
            platform: Target platform ('twitter', 'facebook', 'instagram')
            success: Whether the action was successful
            details: Additional details about the action
        """
        if details is None:
            details = {}

        details['platform'] = platform

        self.log_action(
            action_type=action_type,
            component=f'{platform}_poster',
            success=success,
            details=details
        )

    def log_odoo_action(self, action_type: str, success: bool, details: Dict[str, Any] = None):
        """
        Log Odoo integration actions.

        Args:
            action_type: Type of Odoo action (e.g., 'invoice_created', 'transaction_read', 'connection_success')
            success: Whether the action was successful
            details: Additional details about the action
        """
        self.log_action(
            action_type=action_type,
            component='odoo_integration',
            success=success,
            details=details or {}
        )

    def log_weekly_audit(self, action_type: str, success: bool, details: Dict[str, Any] = None):
        """
        Log weekly audit actions.

        Args:
            action_type: Type of audit action (e.g., 'audit_generated', 'report_saved', 'data_collected')
            success: Whether the action was successful
            details: Additional details about the action
        """
        self.log_action(
            action_type=action_type,
            component='weekly_audit',
            success=success,
            details=details or {}
        )

    def log_rate_limit_event(self, service: str, limit_type: str, current_count: int, max_limit: int):
        """
        Log rate limit events.

        Args:
            service: Service being rate limited (e.g., 'twitter', 'facebook', 'odoo')
            limit_type: Type of limit (e.g., 'daily_posts', 'invoice_creation')
            current_count: Current count toward the limit
            max_limit: Maximum allowed limit
        """
        details = {
            'service': service,
            'limit_type': limit_type,
            'current_count': current_count,
            'max_limit': max_limit,
            'component': 'rate_limiter'
        }

        self.log_action(
            action_type='rate_limit_event',
            component='rate_limiter',
            success=(current_count <= max_limit),
            details=details
        )

    def log_approval_workflow(self, action_type: str, item_type: str, success: bool, details: Dict[str, Any] = None):
        """
        Log approval workflow actions.

        Args:
            action_type: Type of approval action (e.g., 'item_approved', 'item_rejected', 'item_processed')
            item_type: Type of item being approved (e.g., 'social_media_post', 'invoice', 'task_result')
            success: Whether the action was successful
            details: Additional details about the action
        """
        if details is None:
            details = {}

        details['item_type'] = item_type

        self.log_action(
            action_type=action_type,
            component='approved_watcher',
            success=success,
            details=details
        )

    def get_audit_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get a summary of audit trail for the specified number of days.

        Args:
            days: Number of days to include in the summary (default: 7)

        Returns:
            Dictionary with audit summary
        """
        from datetime import timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()

        # Read the main audit log
        main_log_path = self.logs_path / "audit_trail.json"
        if not main_log_path.exists():
            return {
                'period': f'Last {days} days',
                'total_entries': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'by_component': {},
                'by_action_type': {},
                'errors': []
            }

        try:
            with open(main_log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)

            if not isinstance(logs, list):
                logs = []

            # Filter logs by date
            recent_logs = [
                log for log in logs
                if log.get('timestamp', '').startswith(cutoff_date[:4])  # Year match
            ]

            # Calculate summary
            total_entries = len(recent_logs)
            successful_actions = len([log for log in recent_logs if log.get('success', False)])
            failed_actions = total_entries - successful_actions

            # Group by component
            by_component = {}
            for log in recent_logs:
                comp = log.get('component', 'unknown')
                if comp not in by_component:
                    by_component[comp] = {'total': 0, 'success': 0, 'failures': 0}

                by_component[comp]['total'] += 1
                if log.get('success', False):
                    by_component[comp]['success'] += 1
                else:
                    by_component[comp]['failures'] += 1

            # Group by action type
            by_action_type = {}
            for log in recent_logs:
                action_type = log.get('action_type', 'unknown')
                if action_type not in by_action_type:
                    by_action_type[action_type] = 0
                by_action_type[action_type] += 1

            # Collect errors
            errors = [log for log in recent_logs if not log.get('success', False)]

            return {
                'period': f'Last {days} days',
                'total_entries': total_entries,
                'successful_actions': successful_actions,
                'failed_actions': failed_actions,
                'by_component': by_component,
                'by_action_type': by_action_type,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Error generating audit summary: {e}")
            return {
                'period': f'Last {days} days',
                'total_entries': 0,
                'successful_actions': 0,
                'failed_actions': 0,
                'by_component': {},
                'by_action_type': {},
                'errors': [f"Error generating summary: {str(e)}"]
            }


# Global audit trail logger instance
audit_trail_logger = AuditTrailLogger()


def get_audit_trail_logger() -> AuditTrailLogger:
    """Get the global audit trail logger instance."""
    return audit_trail_logger
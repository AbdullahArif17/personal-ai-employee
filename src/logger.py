'''
Logging utility for audit trail compliance in the Personal AI Employee system.
'''

import logging
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, log_file: str = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with audit trail compliance for the Personal AI Employee system.

    Args:
        name: Name of the logger
        log_file: Path to log file (optional, defaults to daily log in vault)
        level: Logging level (default INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create formatter for audit trail compliance
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Determine log file path
    if not log_file:
        # Use vault path from environment or default
        vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        logs_dir = Path(vault_path) / 'Logs'

        # Create logs directory if it doesn't exist
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create daily log file
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f'{today}.log'

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create console handler for real-time monitoring
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Set the logger level to the lowest level to ensure all messages are processed
    # The handlers will filter based on their own levels
    logger.setLevel(logging.DEBUG)

    return logger

def log_action(action_type: str, details: dict, success: bool = True, error_details: str = None):
    """
    Log an action for audit trail compliance.

    Args:
        action_type: Type of action being logged (e.g., 'social_media_post', 'invoice_creation', 'task_processing')
        details: Dictionary containing details about the action
        success: Whether the action was successful
        error_details: Details about any errors if action failed
    """
    # Import here to avoid circular imports
    logger_instance = setup_logger('audit_trail')

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action_type': action_type,
        'success': success,
        'details': details
    }

    if error_details:
        log_entry['error'] = error_details

    status = "SUCCESS" if success else "FAILED"
    logger_instance.info(f"AUDIT TRAIL - {action_type} - {status} - {log_entry}")

class AuditLogger:
    """
    Specialized logger for audit trail compliance with structured logging.
    """

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.logger = setup_logger(f'audit.{component_name}')

    def log_task_processing(self, task_id: str, iteration: int, status: str, result: str = None):
        """
        Log task processing event.

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
            'component': self.component_name
        }

        if result:
            details['result_length'] = len(result)

        self.logger.info(f"TASK_PROCESSING - {task_id} - Iteration {iteration} - {status.upper()}")
        log_action('task_processing', details, success=(status != 'failed'))

    def log_external_action(self, action_type: str, target: str, success: bool, details: dict = None):
        """
        Log external action (social media post, invoice creation, etc.).

        Args:
            action_type: Type of external action
            target: Target of the action (e.g., 'Twitter', 'Odoo', 'Facebook')
            success: Whether the action was successful
            details: Additional details about the action
        """
        log_details = {
            'action_type': action_type,
            'target': target,
            'component': self.component_name
        }

        if details:
            log_details.update(details)

        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"EXTERNAL_ACTION - {action_type} - {target} - {status}")

        log_action(action_type, log_details, success=success)

    def log_rate_limit_event(self, service: str, limit_type: str, current_count: int, max_limit: int):
        """
        Log rate limit events.

        Args:
            service: Service being rate limited (e.g., 'Twitter', 'Facebook', 'Odoo')
            limit_type: Type of limit (e.g., 'daily_posts', 'invoice_creation')
            current_count: Current count toward the limit
            max_limit: Maximum allowed limit
        """
        details = {
            'service': service,
            'limit_type': limit_type,
            'current_count': current_count,
            'max_limit': max_limit,
            'component': self.component_name
        }

        self.logger.info(f"RATE_LIMIT - {service} - {limit_type} - {current_count}/{max_limit}")
        log_action('rate_limit_check', details, success=(current_count <= max_limit))
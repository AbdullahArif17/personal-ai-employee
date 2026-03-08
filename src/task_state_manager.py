'''
Task state manager for the Personal AI Employee system.
Manages state tracking for tasks in the Ralph Wiggum Loop.
'''

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
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

logger = setup_logger('task_state_manager')

class TaskStateManager:
    """
    Manages the state of tasks in the Ralph Wiggum Loop.
    Tracks attempts, status, timestamps, and results for each task.
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the task state manager.

        Args:
            storage_path: Path to store task state data (defaults to vault/Logs/task_states.json)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Use vault path from environment or default
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
            self.storage_path = Path(vault_path) / 'Logs' / 'ralph_task_states.json'

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing task states
        self.task_states = self._load_states()

    def _load_states(self) -> Dict[str, Dict[str, Any]]:
        """Load task states from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    else:
                        logger.warning(f"Invalid task state data format in {self.storage_path}, initializing empty")
                        return {}
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading task states: {e}")
                return {}
        return {}

    def _save_states(self):
        """Save task states to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.task_states, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Error saving task states: {e}")

    def initialize_task(self, task_id: str) -> Dict[str, Any]:
        """
        Initialize state for a new task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            Initial state dictionary for the task
        """
        now = datetime.now().isoformat()
        initial_state = {
            'task_id': task_id,
            'attempts': 0,
            'status': 'new',
            'created_at': now,
            'last_attempt': None,
            'result': None,
            'last_updated': now
        }

        self.task_states[task_id] = initial_state
        self._save_states()

        logger.debug(f"Initialized state for task: {task_id}")
        return initial_state

    def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            State dictionary for the task, or None if not found
        """
        return self.task_states.get(task_id)

    def update_task_state(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update the state of a task with new information.

        Args:
            task_id: Unique identifier for the task
            updates: Dictionary of updates to apply to the task state

        Returns:
            True if update was successful, False otherwise
        """
        if task_id not in self.task_states:
            logger.warning(f"Attempted to update non-existent task: {task_id}")
            return False

        # Apply updates
        for key, value in updates.items():
            self.task_states[task_id][key] = value

        # Update last_updated timestamp
        self.task_states[task_id]['last_updated'] = datetime.now().isoformat()

        self._save_states()
        logger.debug(f"Updated state for task: {task_id}")
        return True

    def increment_attempt(self, task_id: str) -> bool:
        """
        Increment the attempt count for a task.

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if increment was successful, False otherwise
        """
        if task_id not in self.task_states:
            logger.warning(f"Attempted to increment attempt for non-existent task: {task_id}")
            return False

        self.task_states[task_id]['attempts'] += 1
        self.task_states[task_id]['last_attempt'] = datetime.now().isoformat()
        self.task_states[task_id]['last_updated'] = datetime.now().isoformat()

        self._save_states()
        logger.debug(f"Incremented attempt for task: {task_id} (now {self.task_states[task_id]['attempts']})")
        return True

    def is_task_completed(self, task_id: str) -> bool:
        """
        Check if a task is completed.

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if task is completed, False otherwise
        """
        state = self.get_task_state(task_id)
        if not state:
            return False

        return state.get('status') == 'completed'

    def is_task_failed(self, task_id: str) -> bool:
        """
        Check if a task has failed (exceeded max attempts or timeout).

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if task has failed, False otherwise
        """
        state = self.get_task_state(task_id)
        if not state:
            return False

        status = state.get('status')
        return status in ['failed_max_attempts', 'failed_timeout', 'failed_exception']

    def is_task_active(self, task_id: str) -> bool:
        """
        Check if a task is currently active (not completed or failed).

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if task is active, False otherwise
        """
        return not (self.is_task_completed(task_id) or self.is_task_failed(task_id))

    def is_max_attempts_reached(self, task_id: str, max_attempts: int) -> bool:
        """
        Check if a task has reached the maximum number of attempts.

        Args:
            task_id: Unique identifier for the task
            max_attempts: Maximum number of allowed attempts

        Returns:
            True if max attempts reached, False otherwise
        """
        state = self.get_task_state(task_id)
        if not state:
            return False

        return state.get('attempts', 0) >= max_attempts

    def is_task_timed_out(self, task_id: str, max_duration_hours: int) -> bool:
        """
        Check if a task has exceeded the maximum duration.

        Args:
            task_id: Unique identifier for the task
            max_duration_hours: Maximum duration in hours

        Returns:
            True if task is timed out, False otherwise
        """
        state = self.get_task_state(task_id)
        if not state:
            return False

        created_at_str = state.get('created_at')
        if not created_at_str:
            return False

        try:
            created_at = datetime.fromisoformat(created_at_str)
            max_duration = timedelta(hours=max_duration_hours)
            return datetime.now() - created_at > max_duration
        except ValueError:
            logger.error(f"Invalid timestamp format for task {task_id}: {created_at_str}")
            return False

    def cleanup_expired_tasks(self) -> int:
        """
        Clean up tasks that have expired (timed out) but weren't properly marked as failed.

        Returns:
            Number of expired tasks cleaned up
        """
        now = datetime.now()
        expired_tasks = []

        for task_id, state in self.task_states.items():
            created_at_str = state.get('created_at')
            if not created_at_str:
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str)
                # Use 24 hours as default timeout if not specified in state
                max_duration = timedelta(hours=24)

                if now - created_at > max_duration and state.get('status') != 'completed':
                    expired_tasks.append(task_id)
            except ValueError:
                logger.error(f"Invalid timestamp format for task {task_id}: {created_at_str}")
                continue

        # Mark expired tasks as timed out
        for task_id in expired_tasks:
            self.update_task_state(task_id, {
                'status': 'failed_timeout',
                'last_updated': datetime.now().isoformat()
            })
            logger.info(f"Marked expired task as timed out: {task_id}")

        return len(expired_tasks)

    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tracked tasks.

        Returns:
            Dictionary of all task states
        """
        return self.task_states.copy()

    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active tasks (not completed or failed).

        Returns:
            Dictionary of active task states
        """
        active_tasks = {}
        for task_id, state in self.task_states.items():
            if self.is_task_active(task_id):
                active_tasks[task_id] = state
        return active_tasks

    def remove_task(self, task_id: str) -> bool:
        """
        Remove a task from tracking (e.g., after completion or failure).

        Args:
            task_id: Unique identifier for the task

        Returns:
            True if removal was successful, False otherwise
        """
        if task_id in self.task_states:
            del self.task_states[task_id]
            self._save_states()
            logger.debug(f"Removed task from tracking: {task_id}")
            return True
        else:
            logger.warning(f"Attempted to remove non-existent task: {task_id}")
            return False


# Global task state manager instance
task_state_manager = TaskStateManager()


def get_task_state_manager() -> TaskStateManager:
    """Get the global task state manager instance."""
    return task_state_manager
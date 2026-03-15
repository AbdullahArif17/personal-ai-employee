'''
Ralph Wiggum Loop for the Personal AI Employee system.
Monitors Needs_Action folder and processes tasks with AI, retrying up to 10 times.
'''

import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ai_utils import get_ai_processor
from logger import setup_logger, AuditLogger
from config import get_config
from file_utils import get_file_utils

logger = setup_logger('ralph_loop')
audit_logger = AuditLogger('ralph_loop')
config = get_config()
file_utils = get_file_utils()

class RalphLoopHandler(FileSystemEventHandler):
    """Handles file system events for the Ralph Wiggum Loop."""

    def __init__(self):
        super().__init__()
        self.task_states = {}  # Track task states in memory
        self.load_task_states()  # Load any existing state

    def load_task_states(self):
        """Load task states from file if it exists."""
        vault_path = Path(config.vault_path)
        state_file = vault_path / "Logs" / "ralph_task_states.json"

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    self.task_states = json.load(f)
                logger.info(f"Loaded {len(self.task_states)} task states from file")
            except Exception as e:
                logger.error(f"Error loading task states: {e}")

    def save_task_states(self):
        """Save task states to file."""
        vault_path = Path(config.vault_path)
        state_file = vault_path / "Logs" / "ralph_task_states.json"

        try:
            # Create directory if it doesn't exist
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, 'w') as f:
                json.dump(self.task_states, f, indent=2, default=str)
            logger.info(f"Saved {len(self.task_states)} task states to file")
        except Exception as e:
            logger.error(f"Error saving task states: {e}")

    def on_created(self, event):
        """Handle file creation events in the Needs_Action folder."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.parent.name == "Needs_Action":
            logger.info(f"New task detected: {file_path.name}")
            self.process_task(file_path)

    def on_modified(self, event):
        """Handle file modification events in the Needs_Action folder."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.parent.name == "Needs_Action":
            # Only process if it's not already being processed
            if file_path.name not in self.task_states or \
               self.task_states[file_path.name]['status'] != 'processing':
                logger.info(f"Modified task detected: {file_path.name}")
                self.process_task(file_path)

    def process_task(self, file_path: Path):
        """
        Process a task file with AI, retrying up to 10 times if incomplete.

        Args:
            file_path: Path to the task file to process
        """
        task_id = file_path.name

        # Initialize task state if not exists
        if task_id not in self.task_states:
            self.task_states[task_id] = {
                'task_id': task_id,
                'attempts': 0,
                'status': 'new',
                'created_at': datetime.now().isoformat(),
                'last_attempt': None,
                'result': None
            }

        task_state = self.task_states[task_id]

        # Check if we've exceeded max attempts
        if task_state['attempts'] >= config.max_retry_attempts:
            logger.warning(f"Task {task_id} exceeded max retry attempts ({config.max_retry_attempts})")
            audit_logger.log_task_processing(task_id, task_state['attempts'], 'failed_max_attempts')

            if not config.dry_run:
                # Move to Done with failure note
                result_content = f"FAILED: Task exceeded maximum retry attempts ({config.max_retry_attempts})\n\nOriginal content:\n"
                original_content = file_utils.read_file_content(file_path) or ""
                result_content += original_content

                # Create a new file in Done with failure indication
                failed_file_path = file_path.with_name(f"FAILED_{task_id}")
                file_utils.write_file_content(failed_file_path, result_content)

                # Remove original task file
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.error(f"Error removing task file {task_id}: {e}")

            self.save_task_states()
            return

        # Check if we've exceeded max duration
        created_at = datetime.fromisoformat(task_state['created_at'])
        max_duration = timedelta(hours=config.max_retry_duration_hours)
        if datetime.now() - created_at > max_duration:
            logger.warning(f"Task {task_id} exceeded max duration ({config.max_retry_duration_hours} hours)")
            audit_logger.log_task_processing(task_id, task_state['attempts'], 'failed_timeout')

            if not config.dry_run:
                # Move to Done with timeout note
                result_content = f"FAILED: Task exceeded maximum processing duration ({config.max_retry_duration_hours} hours)\n\nOriginal content:\n"
                original_content = file_utils.read_file_content(file_path) or ""
                result_content += original_content

                # Create a new file in Done with failure indication
                timeout_file_path = file_path.with_name(f"TIMEOUT_{task_id}")
                file_utils.write_file_content(timeout_file_path, result_content)

                # Remove original task file
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.error(f"Error removing task file {task_id}: {e}")

            self.save_task_states()
            return

        # Update task state
        task_state['status'] = 'processing'
        task_state['attempts'] += 1
        task_state['last_attempt'] = datetime.now().isoformat()
        self.save_task_states()

        logger.info(f"Processing task {task_id}, attempt {task_state['attempts']}")
        audit_logger.log_task_processing(task_id, task_state['attempts'], 'started')

        try:
            import time
            start_time = time.time()

            # Read the task content
            task_content = file_utils.read_file_content(file_path)
            if not task_content:
                logger.error(f"Could not read content from task {task_id}")
                audit_logger.log_task_processing(task_id, task_state['attempts'], 'failed_read')
                return

            # Process with AI
            ai_processor = get_ai_processor()
            result = ai_processor.generate_content(
                prompt=f"Process the following task and provide a complete response:\n\n{task_content}",
                context=None
            )

            processing_time = time.time() - start_time
            if processing_time > 30:  # 30 second threshold
                logger.warning(f"Task {task_id} took {processing_time:.2f}s to process (threshold: 30s)")
                audit_logger.log_task_processing(task_id, task_state['attempts'], 'slow_processing', f"Took {processing_time:.2f}s")

            if not result:
                logger.error(f"AI failed to generate content for task {task_id}")
                audit_logger.log_task_processing(task_id, task_state['attempts'], 'failed_ai')
                return

            # Validate if the task is complete
            is_complete = ai_processor.validate_completion(task_content, result)

            if is_complete:
                logger.info(f"Task {task_id} completed successfully on attempt {task_state['attempts']}")
                audit_logger.log_task_processing(task_id, task_state['attempts'], 'completed', result)

                if not config.dry_run:
                    # Move the file to Done folder with the result
                    result_content = f"COMPLETED:\n{result}\n\nOriginal task:\n{task_content}"
                    done_file_path = Path(config.vault_path) / "Done" / task_id
                    file_utils.write_file_content(done_file_path, result_content)

                    # Remove the original task file
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logger.error(f"Error removing task file {task_id}: {e}")

                # Update task state
                task_state['status'] = 'completed'
                task_state['result'] = result
                self.task_states.pop(task_id, None)  # Remove completed task from tracking
                self.save_task_states()

            else:
                logger.info(f"Task {task_id} not complete, will retry. Attempt {task_state['attempts']}/{config.max_retry_attempts}")
                audit_logger.log_task_processing(task_id, task_state['attempts'], 'retry', result)

                # Update task state
                task_state['status'] = 'needs_retry'
                task_state['result'] = result
                self.save_task_states()

                if not config.dry_run:
                    # Update the file with the AI's response so far
                    updated_content = f"PROGRESS (attempt {task_state['attempts']}):\n{result}\n\nOriginal task:\n{task_content}"
                    file_utils.write_file_content(file_path, updated_content)

        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            audit_logger.log_task_processing(task_id, task_state['attempts'], 'failed_exception')

            # Update task state
            task_state['status'] = 'error'
            self.save_task_states()


class RalphLoop:
    """Ralph Wiggum Loop implementation for autonomous task completion."""

    def __init__(self, vault_path: str = None, dry_run: bool = None):
        """
        Initialize the Ralph Wiggum Loop.

        Args:
            vault_path: Path to the vault (uses config if not provided)
            dry_run: Whether to run in dry-run mode (uses config if not provided)
        """
        self.vault_path = Path(vault_path or config.vault_path)

        # Use provided dry_run, otherwise get from config
        if dry_run is not None:
            self.dry_run = dry_run
        else:
            self.dry_run = config.dry_run

        self.needs_action_path = self.vault_path / "Needs_Action"
        self.observer = Observer()
        self.handler = RalphLoopHandler()

    def start(self):
        """Start the Ralph Wiggum Loop."""
        if not self.needs_action_path.exists():
            logger.error(f"Needs_Action folder does not exist: {self.needs_action_path}")
            raise FileNotFoundError(f"Needs_Action folder does not exist: {self.needs_action_path}")

        # Schedule the event handler for the Needs_Action directory
        self.observer.schedule(self.handler, str(self.needs_action_path), recursive=False)

        # Start the observer
        self.observer.start()

        status_msg = f"Ralph Wiggum Loop started, monitoring: {self.needs_action_path}"
        logger.info(status_msg)
        audit_logger.log_external_action("ralph_start", "loop", True, {"path": str(self.needs_action_path), "dry_run": self.dry_run})

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping Ralph Wiggum Loop...")
            self.stop()
        except Exception as e:
            logger.error(f"Unexpected error in Ralph Wiggum Loop: {e}")
            audit_logger.log_external_action("ralph_unexpected_error", "loop", False, {"error": str(e)})
            self.stop()

    def stop(self):
        """Stop the Ralph Wiggum Loop."""
        self.observer.stop()
        self.observer.join()
        logger.info("Ralph Wiggum Loop stopped")
        audit_logger.log_external_action("ralph_stop", "loop", True)


def main():
    """Main function to run the Ralph Wiggum Loop."""
    # Get configuration from environment or use defaults
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Create the Ralph Loop instance
    ralph_loop = RalphLoop(vault_path)

    # Start watching
    try:
        ralph_loop.start()
    except KeyboardInterrupt:
        print("\nStopping Ralph Wiggum Loop...")
        ralph_loop.stop()


if __name__ == "__main__":
    main()
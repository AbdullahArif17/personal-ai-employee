"""
Base watcher class for the Personal AI Employee system.
Defines the interface for filesystem watchers.
"""

import abc
import logging
from pathlib import Path
from typing import Optional


class BaseWatcher(abc.ABC):
    """
    Abstract base class for filesystem watchers in the Personal AI Employee system.
    """

    def __init__(self, vault_path: str = "./AI_Employee_Vault", dry_run: bool = True):
        """
        Initialize the base watcher.

        Args:
            vault_path: Path to the AI Employee vault
            dry_run: If True, perform dry runs without making actual changes
        """
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the watcher."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers if logger already exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    @abc.abstractmethod
    def start(self) -> None:
        """
        Start the filesystem watcher.
        This method should be implemented by subclasses.
        """
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """
        Stop the filesystem watcher.
        This method should be implemented by subclasses.
        """
        pass

    def log_action(self, action: str, details: str) -> None:
        """
        Log an action performed by the watcher.

        Args:
            action: The action being performed
            details: Additional details about the action
        """
        log_msg = f"{action}: {details}"
        self.logger.info(log_msg)

        if self.dry_run:
            self.logger.info("(DRY RUN - no actual changes made)")
'''
Rate limiter utility for the Personal AI Employee system.
Implements tracking for Twitter (5/day), Facebook (3/day), Instagram (3/day), and Odoo (10/day).
'''

import os
import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger

logger = setup_logger('rate_limiter')

class RateLimiter:
    """
    Rate limiter utility that tracks usage against defined limits for various services.
    Tracks daily limits for Twitter (5/day), Facebook (3/day), Instagram (3/day), and Odoo (10/day).
    """

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the rate limiter.

        Args:
            storage_path: Path to store rate limit data (defaults to vault/Logs/rate_limits.json)
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # Use vault path from environment or default
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
            self.storage_path = Path(vault_path) / 'Logs' / 'rate_limits.json'

        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing rate limit data
        self.data = self._load_data()

        # Define default limits
        self.default_limits = {
            'twitter': 5,      # 5 posts per day
            'facebook': 3,     # 3 posts per day
            'instagram': 3,    # 3 posts per day
            'odoo': 10         # 10 invoice creations per day
        }

    def _load_data(self) -> Dict:
        """Load rate limit data from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Clean up old entries (older than 2 days to ensure we only track current and previous day)
                    today = datetime.now().date().isoformat()
                    yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()

                    cleaned_data = {}
                    for service, service_data in data.items():
                        cleaned_data[service] = {}
                        for date_str, count in service_data.items():
                            if date_str in [today, yesterday]:
                                cleaned_data[service][date_str] = count

                    return cleaned_data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading rate limit data: {e}")
                return {}
        return {}

    def _save_data(self):
        """Save rate limit data to storage."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving rate limit data: {e}")

    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        return datetime.now().date().isoformat()

    def increment_usage(self, service: str) -> bool:
        """
        Increment usage for a service and check if within limits.

        Args:
            service: Service name (twitter, facebook, instagram, odoo)

        Returns:
            True if within limits, False if limit exceeded
        """
        service = service.lower()
        current_date = self._get_current_date()

        # Initialize service data if not exists
        if service not in self.data:
            self.data[service] = {}

        # Reset count if it's a new day
        if current_date not in self.data[service]:
            self.data[service][current_date] = 0

        # Get current limit for the service
        limit = self.default_limits.get(service, 100)  # Default to 100 if not specified

        # Check if we're within limits
        current_count = self.data[service][current_date]
        if current_count >= limit:
            logger.info(f"Rate limit exceeded for {service}: {current_count}/{limit}")
            return False

        # Increment usage
        self.data[service][current_date] += 1
        self._save_data()

        current_count_after_increment = self.data[service][current_date]
        logger.info(f"Incremented usage for {service}: {current_count_after_increment}/{limit}")

        return True

    def get_usage(self, service: str) -> tuple[int, int]:
        """
        Get current usage and limit for a service.

        Args:
            service: Service name (twitter, facebook, instagram, odoo)

        Returns:
            Tuple of (current_count, limit)
        """
        service = service.lower()
        current_date = self._get_current_date()

        current_count = self.data.get(service, {}).get(current_date, 0)
        limit = self.default_limits.get(service, 100)  # Default to 100 if not specified

        return current_count, limit

    def is_within_limit(self, service: str) -> bool:
        """
        Check if a service is within its rate limit.

        Args:
            service: Service name (twitter, facebook, instagram, odoo)

        Returns:
            True if within limits, False otherwise
        """
        current_count, limit = self.get_usage(service)
        return current_count < limit

    def reset_daily_counters(self):
        """Reset counters for services that have a new day."""
        current_date = self._get_current_date()

        for service in self.data:
            if current_date not in self.data[service]:
                self.data[service][current_date] = 0

        self._save_data()
        logger.info("Daily rate limit counters reset")


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return rate_limiter
'''
Configuration manager for the Personal AI Employee system.
Handles environment variables and application settings for Gold tier features.
'''

import os
import sys
from pathlib import Path
from typing import Optional

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigManager:
    """
    Centralized configuration manager for the Personal AI Employee system.
    Handles environment variables and application settings for all features.
    """

    def __init__(self):
        """Initialize the configuration manager."""
        self._validate_required_vars()

    def _validate_required_vars(self):
        """Validate that required environment variables are set."""
        # Check if either GEMINI_API_KEY or GOOGLE_API_KEY is set
        if not (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')):
            raise ValueError("Either GEMINI_API_KEY or GOOGLE_API_KEY environment variable must be set")

    @property
    def gemini_api_key(self) -> str:
        """Gemini API key for AI processing."""
        return os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') or ''

    @property
    def vault_path(self) -> str:
        """Path to the AI Employee vault."""
        return os.getenv('VAULT_PATH', './AI_Employee_Vault')

    @property
    def dry_run(self) -> bool:
        """Whether to run in dry-run mode."""
        return os.getenv('DRY_RUN', 'false').lower() == 'true'

    @property
    def log_level(self) -> str:
        """Log level for the application."""
        return os.getenv('LOG_LEVEL', 'INFO')

    # Twitter/X API Configuration
    @property
    def twitter_consumer_key(self) -> Optional[str]:
        """Twitter consumer key."""
        return os.getenv('TWITTER_CONSUMER_KEY')

    @property
    def twitter_consumer_secret(self) -> Optional[str]:
        """Twitter consumer secret."""
        return os.getenv('TWITTER_CONSUMER_SECRET')

    @property
    def twitter_user_access_token(self) -> Optional[str]:
        """Twitter user access token."""
        return os.getenv('TWITTER_USER_ACCESS_TOKEN')

    @property
    def twitter_user_access_secret(self) -> Optional[str]:
        """Twitter user access secret."""
        return os.getenv('TWITTER_USER_ACCESS_SECRET')

    @property
    def twitter_bearer_token(self) -> Optional[str]:
        """Twitter bearer token."""
        return os.getenv('TWITTER_BEARER_TOKEN')

    # Facebook/Instagram API Configuration
    @property
    def facebook_access_token(self) -> Optional[str]:
        """Facebook access token."""
        return os.getenv('FACEBOOK_ACCESS_TOKEN')

    @property
    def facebook_page_id(self) -> Optional[str]:
        """Facebook page ID."""
        return os.getenv('FACEBOOK_PAGE_ID')

    @property
    def instagram_access_token(self) -> Optional[str]:
        """Instagram access token."""
        return os.getenv('INSTAGRAM_ACCESS_TOKEN')

    @property
    def instagram_account_id(self) -> Optional[str]:
        """Instagram account ID."""
        return os.getenv('INSTAGRAM_ACCOUNT_ID')

    # Odoo API Configuration
    @property
    def odoo_url(self) -> Optional[str]:
        """Odoo server URL."""
        return os.getenv('ODOO_URL')

    @property
    def odoo_db(self) -> Optional[str]:
        """Odoo database name."""
        return os.getenv('ODOO_DB')

    @property
    def odoo_username(self) -> Optional[str]:
        """Odoo username."""
        return os.getenv('ODOO_USERNAME')

    @property
    def odoo_password(self) -> Optional[str]:
        """Odoo password."""
        return os.getenv('ODOO_PASSWORD')

    # Twitter/X API Configuration
    @property
    def twitter_consumer_key(self) -> Optional[str]:
        """Twitter consumer key."""
        return os.getenv('TWITTER_CONSUMER_KEY')

    @property
    def twitter_consumer_secret(self) -> Optional[str]:
        """Twitter consumer secret."""
        return os.getenv('TWITTER_CONSUMER_SECRET')

    @property
    def twitter_user_access_token(self) -> Optional[str]:
        """Twitter user access token."""
        return os.getenv('TWITTER_USER_ACCESS_TOKEN')

    @property
    def twitter_user_access_secret(self) -> Optional[str]:
        """Twitter user access secret."""
        return os.getenv('TWITTER_USER_ACCESS_SECRET')

    @property
    def twitter_bearer_token(self) -> Optional[str]:
        """Twitter bearer token."""
        return os.getenv('TWITTER_BEARER_TOKEN')

    # Facebook/Instagram API Configuration
    @property
    def facebook_access_token(self) -> Optional[str]:
        """Facebook access token."""
        return os.getenv('FACEBOOK_ACCESS_TOKEN')

    @property
    def facebook_page_id(self) -> Optional[str]:
        """Facebook page ID."""
        return os.getenv('FACEBOOK_PAGE_ID')

    @property
    def instagram_access_token(self) -> Optional[str]:
        """Instagram access token."""
        return os.getenv('INSTAGRAM_ACCESS_TOKEN')

    @property
    def instagram_account_id(self) -> Optional[str]:
        """Instagram account ID."""
        return os.getenv('INSTAGRAM_ACCOUNT_ID')

    # Rate Limiting Configuration
    @property
    def twitter_daily_limit(self) -> int:
        """Daily limit for Twitter posts."""
        return int(os.getenv('TWITTER_DAILY_LIMIT', '5'))

    @property
    def facebook_daily_limit(self) -> int:
        """Daily limit for Facebook posts."""
        return int(os.getenv('FACEBOOK_DAILY_LIMIT', '3'))

    @property
    def instagram_daily_limit(self) -> int:
        """Daily limit for Instagram posts."""
        return int(os.getenv('INSTAGRAM_DAILY_LIMIT', '3'))

    @property
    def odoo_invoice_daily_limit(self) -> int:
        """Daily limit for Odoo invoice creation."""
        return int(os.getenv('ODOO_INVOICE_DAILY_LIMIT', '10'))

    # Retry Configuration
    @property
    def max_retry_attempts(self) -> int:
        """Maximum number of retry attempts for tasks."""
        return int(os.getenv('MAX_RETRY_ATTEMPTS', '10'))

    @property
    def max_retry_duration_hours(self) -> int:
        """Maximum duration for retry attempts in hours."""
        return int(os.getenv('MAX_RETRY_DURATION_HOURS', '24'))

    # Approval Expiration Configuration
    @property
    def approval_expiration_days(self) -> int:
        """Number of days before unapproved items are auto-rejected."""
        return int(os.getenv('APPROVAL_EXPIRATION_DAYS', '30'))

    # Log Retention Configuration
    @property
    def log_retention_days(self) -> int:
        """Number of days to retain logs."""
        return int(os.getenv('LOG_RETENTION_DAYS', '90'))

    # Rate Limiting Configuration
    @property
    def twitter_daily_limit(self) -> int:
        """Daily limit for Twitter posts."""
        return int(os.getenv('TWITTER_DAILY_LIMIT', '5'))

    @property
    def facebook_daily_limit(self) -> int:
        """Daily limit for Facebook posts."""
        return int(os.getenv('FACEBOOK_DAILY_LIMIT', '3'))

    @property
    def instagram_daily_limit(self) -> int:
        """Daily limit for Instagram posts."""
        return int(os.getenv('INSTAGRAM_DAILY_LIMIT', '3'))

    @property
    def odoo_invoice_daily_limit(self) -> int:
        """Daily limit for Odoo invoice creation."""
        return int(os.getenv('ODOO_INVOICE_DAILY_LIMIT', '10'))

    # Retry Configuration
    @property
    def max_retry_attempts(self) -> int:
        """Maximum number of retry attempts for tasks."""
        return int(os.getenv('MAX_RETRY_ATTEMPTS', '10'))

    @property
    def max_retry_duration_hours(self) -> int:
        """Maximum duration for retry attempts in hours."""
        return int(os.getenv('MAX_RETRY_DURATION_HOURS', '24'))

    # Approval Expiration Configuration
    @property
    def approval_expiration_days(self) -> int:
        """Number of days before unapproved items are auto-rejected."""
        return int(os.getenv('APPROVAL_EXPIRATION_DAYS', '30'))

    # Log Retention Configuration
    @property
    def log_retention_days(self) -> int:
        """Number of days to retain logs."""
        return int(os.getenv('LOG_RETENTION_DAYS', '90'))


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config
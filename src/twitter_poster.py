'''
Twitter/X poster for the Personal AI Employee system.
Generates tweets using AI based on Company_Handbook.md and manages posting workflow.
'''

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .ai_utils import get_ai_processor
    from .logger import setup_logger, AuditLogger
    from .config import get_config
    from .file_utils import get_file_utils
    from .rate_limiter import get_rate_limiter
except ImportError:
    # Fallback for when running as a script directly
    from ai_utils import get_ai_processor
    from logger import setup_logger, AuditLogger
    from config import get_config
    from file_utils import get_file_utils
    from rate_limiter import get_rate_limiter

logger = setup_logger('twitter_poster')
audit_logger = AuditLogger('twitter_poster')
config = get_config()
file_utils = get_file_utils()
rate_limiter = get_rate_limiter()

class TwitterPoster:
    """
    Twitter/X poster implementation for the Personal AI Employee system.
    Generates tweets using AI based on Company_Handbook.md and manages posting workflow.
    """

    def __init__(self):
        """Initialize the Twitter poster."""
        self.ai_processor = get_ai_processor()

    def generate_tweet_from_handbook(self) -> Optional[str]:
        """
        Generate a tweet based on the Company Handbook content.

        Returns:
            Generated tweet content, or None if failed
        """
        try:
            import time
            start_time = time.time()

            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for tweet generation")
                return None

            # Generate tweet using AI
            prompt = f"""
            Based on the following company handbook, generate an engaging tweet (under 280 characters) that represents the company's values and mission:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Please make it professional, engaging, and reflective of the company's identity.
            Include relevant hashtags based on the company's industry and values.
            """

            tweet_content = self.ai_processor.generate_content(prompt)

            generation_time = time.time() - start_time
            if generation_time > 10:  # 10 second threshold
                logger.warning(f"Tweet generation took {generation_time:.2f}s (threshold: 10s)")
                audit_logger.log_external_action("tweet_slow_generation", "twitter", False, {"duration": generation_time})

            if tweet_content:
                # Ensure tweet is within Twitter's character limit
                if len(tweet_content) > 280:
                    tweet_content = tweet_content[:277] + "..."

                logger.info("Successfully generated tweet from company handbook")
                return tweet_content.strip()
            else:
                logger.error("AI failed to generate tweet content")
                return None

        except Exception as e:
            logger.error(f"Error generating tweet from handbook: {e}")
            return None

    def create_tweet_draft(self, content: Optional[str] = None) -> Optional[Path]:
        """
        Create a tweet draft, either from provided content or generated from handbook.

        Args:
            content: Specific content for the tweet (if None, generate from handbook)

        Returns:
            Path to the created draft file, or None if failed
        """
        try:
            if not content:
                content = self.generate_tweet_from_handbook()
                if not content:
                    logger.error("Could not generate tweet content for draft")
                    return None

            # Create draft file in Pending_Approval folder
            draft_path = file_utils.create_draft_file(
                content=content,
                folder="Pending_Approval",
                prefix="twitter_draft"
            )

            if draft_path:
                logger.info(f"Created Twitter draft: {draft_path.name}")
                audit_logger.log_external_action("draft_created", "twitter", True, {"file": draft_path.name})
                return draft_path
            else:
                logger.error("Failed to create Twitter draft file")
                return None

        except Exception as e:
            logger.error(f"Error creating tweet draft: {e}")
            return None

    def post_tweet(self, content: str) -> bool:
        """
        Post a tweet to Twitter/X after validating rate limits.

        Args:
            content: Content to post as a tweet

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check rate limit before posting
            if not rate_limiter.increment_usage('twitter'):
                logger.warning("Twitter rate limit exceeded, cannot post tweet")
                audit_logger.log_rate_limit_event('twitter', 'posts', *rate_limiter.get_usage('twitter'))
                return False

            # Validate content length
            if len(content) > 280:
                content = content[:277] + "..."

            if config.dry_run:
                logger.info(f"(DRY RUN) Would post tweet: {content[:50]}...")
                audit_logger.log_external_action("tweet_dry_run", "twitter", True, {"content_preview": content[:50]})
                return True

            # Import Twitter libraries
            import tweepy

            # Get Twitter credentials
            api_key = config.twitter_api_key
            api_secret = config.twitter_api_secret
            access_token = config.twitter_access_token
            access_token_secret = config.twitter_access_secret
            bearer_token = config.twitter_bearer_token

            if not all([api_key, api_secret, access_token, access_token_secret]):
                logger.error("Missing required Twitter API credentials")
                return False

            # Authenticate with Twitter API v2
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Post the tweet
            response = client.create_tweet(text=content)

            if response.data and 'id' in response.data:
                tweet_id = response.data['id']
                logger.info(f"Successfully posted tweet with ID: {tweet_id}")
                audit_logger.log_external_action("tweet_posted", "twitter", True, {"tweet_id": tweet_id})
                return True
            else:
                logger.error("Failed to post tweet, no ID returned")
                audit_logger.log_external_action("tweet_failed", "twitter", False)
                return False

        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            audit_logger.log_external_action("tweet_error", "twitter", False, {"error": str(e)})
            return False

    def process_approved_tweet(self, file_path: Path) -> bool:
        """
        Process an approved tweet file and post it to Twitter.

        Args:
            file_path: Path to the approved tweet file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the approved content
            content = file_utils.read_file_content(file_path)
            if not content:
                logger.error(f"Could not read content from approved tweet: {file_path.name}")
                return False

            # Post to Twitter
            success = self.post_tweet(content)

            if success:
                # Move to Done folder after successful posting
                file_utils.move_file(file_path, "Done")
                logger.info(f"Successfully processed and posted approved tweet: {file_path.name}")
            else:
                logger.error(f"Failed to post approved tweet: {file_path.name}")
                # Optionally, move to a failed folder or keep in approved for retry
                failed_path = file_path.with_name(f"FAILED_{file_path.name}")
                file_utils.move_file(file_path, "Done")  # Move to done even if posting failed to prevent repeated attempts

            return success

        except Exception as e:
            logger.error(f"Error processing approved tweet {file_path.name}: {e}")
            audit_logger.log_external_action("process_error", "twitter", False, {
                "file": file_path.name,
                "error": str(e)
            })
            return False

    def generate_and_draft_tweet(self) -> bool:
        """
        Generate a tweet from the company handbook and create a draft.

        Returns:
            True if successful, False otherwise
        """
        try:
            draft_path = self.create_tweet_draft()
            return draft_path is not None
        except Exception as e:
            logger.error(f"Error generating and drafting tweet: {e}")
            return False


def main():
    """Main function to demonstrate Twitter poster usage."""
    try:
        poster = TwitterPoster()

        # Example: Generate a tweet from the company handbook
        success = poster.generate_and_draft_tweet()

        if success:
            print("Tweet drafted successfully and placed in Pending_Approval folder for review")
        else:
            print("Failed to generate and draft tweet")
    except Exception as e:
        logger.error(f"Error in Twitter poster main: {e}")
        audit_logger.log_external_action("twitter_main_error", "twitter", False, {"error": str(e)})
        raise


if __name__ == "__main__":
    main()
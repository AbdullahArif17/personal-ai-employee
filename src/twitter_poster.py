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

    def generate_business_tip_tweet(self) -> Optional[str]:
        """
        Generate a business tip tweet based on the Company Handbook content.

        Returns:
            Generated tweet content, or None if failed
        """
        try:
            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for tweet generation")
                return None

            # Generate tweet using AI
            prompt = f"""
            Based on the following company handbook, generate an engaging business tip tweet (under 280 characters) that represents the company's values and mission:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Please make it professional, engaging, and reflective of the company's identity.
            Include relevant hashtags based on the company's industry and values.
            Focus on providing actionable business advice.
            """

            tweet_content = self.ai_processor.generate_content(prompt)

            if tweet_content:
                # Ensure tweet is within Twitter's character limit
                if len(tweet_content) > 280:
                    tweet_content = tweet_content[:277] + "..."

                logger.info("Successfully generated business tip tweet from company handbook")
                return tweet_content.strip()
            else:
                logger.error("AI failed to generate business tip tweet content")
                return None

        except Exception as e:
            logger.error(f"Error generating business tip tweet from handbook: {e}")
            return None

    def generate_thread_tweets(self) -> Optional[str]:
        """
        Generate a thread of 5 tweets about AI automation based on the Company Handbook content.

        Returns:
            Generated thread content (5 tweets separated by newlines), or None if failed
        """
        try:
            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for thread generation")
                return None

            # Generate thread using AI
            prompt = f"""
            Based on the following company handbook, generate a thread of 5 tweets about AI automation and business efficiency:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Each tweet should be under 280 characters and focus on a different aspect of AI automation.
            Make the thread engaging, informative, and cohesive.
            Include relevant hashtags based on the company's industry and values.
            Number the tweets in the thread (1/5, 2/5, etc.).
            """

            thread_content = self.ai_processor.generate_content(prompt)

            if thread_content:
                # Ensure each tweet in the thread is within Twitter's character limit
                tweets = thread_content.split('\n')
                processed_tweets = []
                for tweet in tweets:
                    if len(tweet.strip()) > 0:
                        if len(tweet) > 280:
                            tweet = tweet[:277] + "..."
                        processed_tweets.append(tweet.strip())

                final_content = '\n'.join(processed_tweets)
                logger.info("Successfully generated thread tweets from company handbook")
                return final_content
            else:
                logger.error("AI failed to generate thread tweet content")
                return None

        except Exception as e:
            logger.error(f"Error generating thread tweets from handbook: {e}")
            return None

    def generate_engagement_question_tweet(self) -> Optional[str]:
        """
        Generate an engagement question tweet based on the Company Handbook content.

        Returns:
            Generated tweet content, or None if failed
        """
        try:
            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for engagement question generation")
                return None

            # Generate engagement question using AI
            prompt = f"""
            Based on the following company handbook, generate an engaging question tweet (under 280 characters) that encourages interaction and discussion:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Please make it thought-provoking, relevant to business professionals, and encourage responses.
            Include relevant hashtags based on the company's industry and values.
            End with a question that invites engagement.
            """

            tweet_content = self.ai_processor.generate_content(prompt)

            if tweet_content:
                # Ensure tweet is within Twitter's character limit
                if len(tweet_content) > 280:
                    tweet_content = tweet_content[:277] + "..."

                logger.info("Successfully generated engagement question tweet from company handbook")
                return tweet_content.strip()
            else:
                logger.error("AI failed to generate engagement question tweet content")
                return None

        except Exception as e:
            logger.error(f"Error generating engagement question tweet from handbook: {e}")
            return None

    def create_tweet_draft(self, content: str, tweet_type: str) -> Optional[Path]:
        """
        Create a tweet draft file in the Pending_Approval folder.

        Args:
            content: Tweet content to save
            tweet_type: Type of tweet ('tip', 'thread', 'question')

        Returns:
            Path to the created draft file, or None if failed
        """
        try:
            # Create filename based on type and timestamp
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"TWITTER_{tweet_type}_{date_str}.md"
            filepath = file_utils.pending_approval_path / filename

            # Handle filename conflicts
            counter = 1
            original_filepath = filepath
            while filepath.exists():
                filepath = file_utils.pending_approval_path / f"TWITTER_{tweet_type}_{date_str}_{counter}.md"
                counter += 1

            # Create markdown content with YAML header
            yaml_header = f"""---
action: post_tweet
type: {tweet_type}
generated: {datetime.now().strftime('%Y-%m-%d')}
status: pending_approval
character_count: {len(content)}
---

{content}"""

            # Write the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(yaml_header)

            logger.info(f"Created Twitter draft: {filepath.name}")
            audit_logger.log_external_action("draft_created", "twitter", True, {"file": filepath.name, "type": tweet_type})
            return filepath

        except Exception as e:
            logger.error(f"Error creating Twitter draft: {e}")
            return None

    def generate_and_draft_tweets(self) -> bool:
        """
        Generate all three types of tweets and create drafts.

        Returns:
            True if successful, False otherwise
        """
        try:
            success_count = 0

            # Generate and create business tip tweet draft
            tip_content = self.generate_business_tip_tweet()
            if tip_content:
                tip_draft_path = self.create_tweet_draft(tip_content, "tip")
                if tip_draft_path:
                    success_count += 1
                    logger.info(f"Created business tip tweet draft: {tip_draft_path.name}")

            # Generate and create thread tweet draft
            thread_content = self.generate_thread_tweets()
            if thread_content:
                thread_draft_path = self.create_tweet_draft(thread_content, "thread")
                if thread_draft_path:
                    success_count += 1
                    logger.info(f"Created thread tweet draft: {thread_draft_path.name}")

            # Generate and create engagement question tweet draft
            question_content = self.generate_engagement_question_tweet()
            if question_content:
                question_draft_path = self.create_tweet_draft(question_content, "question")
                if question_draft_path:
                    success_count += 1
                    logger.info(f"Created engagement question tweet draft: {question_draft_path.name}")

            logger.info(f"Successfully created {success_count} Twitter draft(s)")
            return success_count > 0

        except Exception as e:
            logger.error(f"Error generating and drafting tweets: {e}")
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

            # Extract tweet type from YAML header
            tweet_type = "unknown"
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == '---' and i > 0:  # End of YAML header
                    break
                if line.startswith('type:'):
                    tweet_type = line.replace('type:', '').strip()

            # Check rate limit before posting
            if not rate_limiter.increment_usage('twitter'):
                logger.warning("Twitter rate limit exceeded, cannot post tweet")
                audit_logger.log_rate_limit_event('twitter', 'posts', *rate_limiter.get_usage('twitter'))
                return False

            if config.dry_run:
                logger.info(f"(DRY RUN) Would post tweet to Twitter: {content[:50]}...")
                audit_logger.log_external_action("tweet_dry_run", "twitter", True, {"content_preview": content[:50]})
                return True

            # Import Twitter libraries
            import tweepy

            # Get Twitter credentials
            consumer_key = config.twitter_consumer_key
            consumer_secret = config.twitter_consumer_secret
            user_access_token = config.twitter_user_access_token
            user_access_secret = config.twitter_user_access_secret
            bearer_token = config.twitter_bearer_token

            if not all([consumer_key, consumer_secret, user_access_token, user_access_secret, bearer_token]):
                logger.error("Missing required Twitter API credentials")
                return False

            # Authenticate with Twitter API v2
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=user_access_token,
                access_token_secret=user_access_secret
            )

            # Handle thread tweets specially
            if tweet_type == "thread":
                tweets = content.split('\n')
                prev_tweet_id = None

                for tweet_text in tweets:
                    if tweet_text.strip() and not tweet_text.startswith("---") and ":" not in tweet_text[:20]:
                        # Ensure tweet is within Twitter's character limit
                        if len(tweet_text) > 280:
                            tweet_text = tweet_text[:277] + "..."

                        if prev_tweet_id:
                            # Reply to previous tweet in thread
                            response = client.create_tweet(text=tweet_text, in_reply_to_tweet_id=prev_tweet_id)
                        else:
                            # First tweet in thread
                            response = client.create_tweet(text=tweet_text)

                        if response.data and 'id' in response.data:
                            prev_tweet_id = response.data['id']
                        else:
                            logger.error(f"Failed to post thread tweet: {tweet_text[:50]}...")
                            return False
            else:
                # Handle single tweet
                if len(content) > 280:
                    content = content[:277] + "..."

                response = client.create_tweet(text=content)

                if not (response.data and 'id' in response.data):
                    logger.error(f"Failed to post tweet: {file_path.name}")
                    audit_logger.log_external_action("tweet_failed", "twitter", False, {"file": file_path.name})
                    return False

            logger.info(f"Successfully posted tweet to Twitter: {file_path.name}")
            audit_logger.log_external_action("tweet_posted", "twitter", True, {"file": file_path.name, "type": tweet_type})

            # Move to Done folder after successful posting
            file_utils.move_file(file_path, "Done")

            return True

        except Exception as e:
            logger.error(f"Error processing approved tweet {file_path.name}: {e}")
            audit_logger.log_external_action("process_error", "twitter", False, {
                "file": file_path.name,
                "error": str(e)
            })
            return False


def main():
    """Main function to demonstrate Twitter poster usage."""
    try:
        poster = TwitterPoster()

        # Example: Generate all three types of tweets from the company handbook
        success = poster.generate_and_draft_tweets()

        if success:
            print("Twitter drafts created successfully and placed in Pending_Approval folder for review")
        else:
            print("Failed to generate and draft tweets")
    except Exception as e:
        logger.error(f"Error in Twitter poster main: {e}")
        audit_logger.log_external_action("twitter_main_error", "twitter", False, {"error": str(e)})
        raise


if __name__ == "__main__":
    main()
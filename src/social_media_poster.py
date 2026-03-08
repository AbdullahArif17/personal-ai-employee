'''
Social media poster for the Personal AI Employee system.
Generates Facebook and Instagram posts using AI and manages posting workflow.
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

logger = setup_logger('social_media_poster')
audit_logger = AuditLogger('social_media_poster')
config = get_config()
file_utils = get_file_utils()
rate_limiter = get_rate_limiter()

class SocialMediaPoster:
    """
    Social media poster implementation for the Personal AI Employee system.
    Generates Facebook and Instagram posts using AI and manages posting workflow.
    """

    def __init__(self):
        """Initialize the social media poster."""
        self.ai_processor = get_ai_processor()

    def generate_facebook_post_from_handbook(self) -> Optional[str]:
        """
        Generate a Facebook post based on the Company Handbook content.

        Returns:
            Generated Facebook post content, or None if failed
        """
        try:
            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for Facebook post generation")
                return None

            # Generate Facebook post using AI
            prompt = f"""
            Based on the following company handbook, generate an engaging Facebook post that represents the company's values and mission:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Please make it professional, engaging, and reflective of the company's identity.
            Include relevant hashtags based on the company's industry and values.
            Add appropriate emojis to make it more appealing for Facebook audience.
            """

            post_content = self.ai_processor.generate_content(prompt)

            if post_content:
                logger.info("Successfully generated Facebook post from company handbook")
                return post_content.strip()
            else:
                logger.error("AI failed to generate Facebook post content")
                return None

        except Exception as e:
            logger.error(f"Error generating Facebook post from handbook: {e}")
            return None

    def generate_instagram_post_from_handbook(self) -> Optional[str]:
        """
        Generate an Instagram post based on the Company Handbook content.

        Returns:
            Generated Instagram post content, or None if failed
        """
        try:
            # Get company handbook content
            handbook_content = file_utils.get_company_handbook_content()
            if not handbook_content:
                logger.error("Could not get company handbook content for Instagram post generation")
                return None

            # Generate Instagram post using AI
            prompt = f"""
            Based on the following company handbook, generate an engaging Instagram post that represents the company's values and mission:

            {handbook_content[:2000]}  # Limit to first 2000 characters to avoid exceeding AI token limits

            Please make it visually appealing, trendy, and perfect for Instagram audience.
            Include relevant hashtags (at least 5-10) based on the company's industry and values.
            Add appropriate emojis to make it more appealing for Instagram.
            Focus on creating content that encourages likes and shares.
            """

            post_content = self.ai_processor.generate_content(prompt)

            if post_content:
                logger.info("Successfully generated Instagram post from company handbook")
                return post_content.strip()
            else:
                logger.error("AI failed to generate Instagram post content")
                return None

        except Exception as e:
            logger.error(f"Error generating Instagram post from handbook: {e}")
            return None

    def create_facebook_draft(self, content: Optional[str] = None) -> Optional[Path]:
        """
        Create a Facebook post draft, either from provided content or generated from handbook.

        Args:
            content: Specific content for the post (if None, generate from handbook)

        Returns:
            Path to the created draft file, or None if failed
        """
        try:
            if not content:
                content = self.generate_facebook_post_from_handbook()
                if not content:
                    logger.error("Could not generate Facebook post content for draft")
                    return None

            # Create draft file in Pending_Approval folder
            draft_path = file_utils.create_draft_file(
                content=content,
                folder="Pending_Approval",
                prefix="facebook_draft"
            )

            if draft_path:
                logger.info(f"Created Facebook draft: {draft_path.name}")
                audit_logger.log_external_action("draft_created", "facebook", True, {"file": draft_path.name})
                return draft_path
            else:
                logger.error("Failed to create Facebook draft file")
                return None

        except Exception as e:
            logger.error(f"Error creating Facebook draft: {e}")
            return None

    def create_instagram_draft(self, content: Optional[str] = None) -> Optional[Path]:
        """
        Create an Instagram post draft, either from provided content or generated from handbook.

        Args:
            content: Specific content for the post (if None, generate from handbook)

        Returns:
            Path to the created draft file, or None if failed
        """
        try:
            if not content:
                content = self.generate_instagram_post_from_handbook()
                if not content:
                    logger.error("Could not generate Instagram post content for draft")
                    return None

            # Create draft file in Pending_Approval folder
            draft_path = file_utils.create_draft_file(
                content=content,
                folder="Pending_Approval",
                prefix="instagram_draft"
            )

            if draft_path:
                logger.info(f"Created Instagram draft: {draft_path.name}")
                audit_logger.log_external_action("draft_created", "instagram", True, {"file": draft_path.name})
                return draft_path
            else:
                logger.error("Failed to create Instagram draft file")
                return None

        except Exception as e:
            logger.error(f"Error creating Instagram draft: {e}")
            return None

    def post_to_facebook(self, content: str) -> bool:
        """
        Post content to Facebook after validating rate limits.

        Args:
            content: Content to post to Facebook

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check rate limit before posting
            if not rate_limiter.increment_usage('facebook'):
                logger.warning("Facebook rate limit exceeded, cannot post")
                audit_logger.log_rate_limit_event('facebook', 'posts', *rate_limiter.get_usage('facebook'))
                return False

            if config.dry_run:
                logger.info(f"(DRY RUN) Would post to Facebook: {content[:50]}...")
                audit_logger.log_external_action("facebook_dry_run", "facebook", True, {"content_preview": content[:50]})
                return True

            # Import Facebook libraries
            import requests

            # Get Facebook credentials
            access_token = config.facebook_access_token
            page_id = config.facebook_page_id

            if not all([access_token, page_id]):
                logger.error("Missing required Facebook API credentials")
                return False

            # Prepare the post data
            post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            params = {
                'message': content,
                'access_token': access_token
            }

            # Make the POST request
            response = requests.post(post_url, params=params)

            if response.status_code == 200:
                response_data = response.json()
                post_id = response_data.get('id', 'unknown')
                logger.info(f"Successfully posted to Facebook with ID: {post_id}")
                audit_logger.log_external_action("facebook_posted", "facebook", True, {"post_id": post_id})
                return True
            else:
                logger.error(f"Failed to post to Facebook: {response.text}")
                audit_logger.log_external_action("facebook_failed", "facebook", False, {"error": response.text})
                return False

        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            audit_logger.log_external_action("facebook_error", "facebook", False, {"error": str(e)})
            return False

    def post_to_instagram(self, caption: str) -> bool:
        """
        Post content to Instagram after validating rate limits.

        Args:
            caption: Caption to post to Instagram

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check rate limit before posting
            if not rate_limiter.increment_usage('instagram'):
                logger.warning("Instagram rate limit exceeded, cannot post")
                audit_logger.log_rate_limit_event('instagram', 'posts', *rate_limiter.get_usage('instagram'))
                return False

            if config.dry_run:
                logger.info(f"(DRY RUN) Would post to Instagram: {caption[:50]}...")
                audit_logger.log_external_action("instagram_dry_run", "instagram", True, {"content_preview": caption[:50]})
                return True

            # Import Instagram libraries
            import requests

            # Get Instagram credentials
            access_token = config.instagram_access_token
            account_id = config.instagram_account_id

            if not all([access_token, account_id]):
                logger.error("Missing required Instagram API credentials")
                return False

            # For text-only posts, we need to create a media object
            # First, create the media container
            creation_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            creation_params = {
                'caption': caption,
                'access_token': access_token
            }

            # Create the media container
            response = requests.post(creation_url, params=creation_params)

            if response.status_code != 200:
                logger.error(f"Failed to create Instagram media container: {response.text}")
                audit_logger.log_external_action("instagram_creation_failed", "instagram", False, {"error": response.text})
                return False

            response_data = response.json()
            container_id = response_data.get('id')

            if not container_id:
                logger.error("Failed to get container ID from Instagram media creation")
                audit_logger.log_external_action("instagram_no_container", "instagram", False)
                return False

            # Then publish the media
            publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
            publish_params = {
                'creation_id': container_id,
                'access_token': access_token
            }

            publish_response = requests.post(publish_url, params=publish_params)

            if publish_response.status_code == 200:
                publish_data = publish_response.json()
                post_id = publish_data.get('id')
                logger.info(f"Successfully posted to Instagram with ID: {post_id}")
                audit_logger.log_external_action("instagram_posted", "instagram", True, {"post_id": post_id})
                return True
            else:
                logger.error(f"Failed to publish Instagram post: {publish_response.text}")
                audit_logger.log_external_action("instagram_publish_failed", "instagram", False, {"error": publish_response.text})
                return False

        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            audit_logger.log_external_action("instagram_error", "instagram", False, {"error": str(e)})
            return False

    def process_approved_facebook_post(self, file_path: Path) -> bool:
        """
        Process an approved Facebook post file and post it to Facebook.

        Args:
            file_path: Path to the approved Facebook post file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the approved content
            content = file_utils.read_file_content(file_path)
            if not content:
                logger.error(f"Could not read content from approved Facebook post: {file_path.name}")
                return False

            # Post to Facebook
            success = self.post_to_facebook(content)

            if success:
                # Move to Done folder after successful posting
                file_utils.move_file(file_path, "Done")
                logger.info(f"Successfully processed and posted approved Facebook post: {file_path.name}")
            else:
                logger.error(f"Failed to post approved Facebook post: {file_path.name}")
                # Move to Done anyway to prevent repeated attempts
                file_utils.move_file(file_path, "Done")

            return success

        except Exception as e:
            logger.error(f"Error processing approved Facebook post {file_path.name}: {e}")
            audit_logger.log_external_action("facebook_process_error", "facebook", False, {
                "file": file_path.name,
                "error": str(e)
            })
            return False

    def process_approved_instagram_post(self, file_path: Path) -> bool:
        """
        Process an approved Instagram post file and post it to Instagram.

        Args:
            file_path: Path to the approved Instagram post file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read the approved content
            content = file_utils.read_file_content(file_path)
            if not content:
                logger.error(f"Could not read content from approved Instagram post: {file_path.name}")
                return False

            # Post to Instagram
            success = self.post_to_instagram(content)

            if success:
                # Move to Done folder after successful posting
                file_utils.move_file(file_path, "Done")
                logger.info(f"Successfully processed and posted approved Instagram post: {file_path.name}")
            else:
                logger.error(f"Failed to post approved Instagram post: {file_path.name}")
                # Move to Done anyway to prevent repeated attempts
                file_utils.move_file(file_path, "Done")

            return success

        except Exception as e:
            logger.error(f"Error processing approved Instagram post {file_path.name}: {e}")
            audit_logger.log_external_action("instagram_process_error", "instagram", False, {
                "file": file_path.name,
                "error": str(e)
            })
            return False

    def generate_and_draft_social_posts(self) -> bool:
        """
        Generate both Facebook and Instagram posts from the company handbook and create drafts.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate and create Facebook draft
            fb_success = self.create_facebook_draft() is not None

            # Generate and create Instagram draft
            ig_success = self.create_instagram_draft() is not None

            success = fb_success and ig_success

            if success:
                logger.info("Successfully generated and drafted both Facebook and Instagram posts")
            else:
                logger.warning("Failed to generate one or both social media drafts")

            return success

        except Exception as e:
            logger.error(f"Error generating and drafting social media posts: {e}")
            return False


def main():
    """Main function to demonstrate social media poster usage."""
    try:
        poster = SocialMediaPoster()

        # Example: Generate both Facebook and Instagram posts from the company handbook
        success = poster.generate_and_draft_social_posts()

        if success:
            print("Social media posts drafted successfully and placed in Pending_Approval folder for review")
        else:
            print("Failed to generate and draft social media posts")
    except Exception as e:
        logger.error(f"Error in social media poster main: {e}")
        audit_logger.log_external_action("social_media_main_error", "social_media", False, {"error": str(e)})
        raise


if __name__ == "__main__":
    main()
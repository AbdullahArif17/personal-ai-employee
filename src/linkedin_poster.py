"""
LinkedIn poster for the Personal AI Employee system.
Generates and posts business posts to LinkedIn after human approval.
"""
import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Note: Using file-based approach instead of LinkedIn API, so no need for LinkedIn auth import


class LinkedInPoster:
    """LinkedIn poster implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.done_path = self.vault_path / "Done"  # Added this
        self.logs_path = self.vault_path / "Logs"

        # Rate limiting: max 3 posts per day
        self.max_posts_per_day = 3

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file")

        self.client = genai.Client(api_key=api_key)

        # Create directories if they don't exist
        self.pending_approval_path.mkdir(exist_ok=True)
        self.done_path.mkdir(exist_ok=True)  # Added this
        self.logs_path.mkdir(exist_ok=True)

    def generate_post_content(self, topic: Optional[str] = None) -> str:
        """
        Generate LinkedIn post content using Gemini AI.

        Args:
            topic: Specific topic to focus on (optional)

        Returns:
            Generated post content
        """
        if not topic:
            # Generate a general business post based on trending topics
            prompt = """Generate a professional LinkedIn post about a trending business topic.
            The post should be engaging, informative, and encourage professional discussion.
            Keep it under 500 characters and focus on business insights."""
        else:
            # Generate a post based on the specified topic
            prompt = f"""Generate a professional LinkedIn post about {topic}.
            The post should be engaging, informative, and encourage professional discussion.
            Keep it under 500 characters and focus on business insights."""

        try:
            response = self.client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt
            )
            return response.text if response.text else "No content generated"
        except Exception as e:
            print(f"Error generating post with Gemini: {e}")
            return "Sample LinkedIn post content"

    def save_post_draft(self, content: str, topic: str) -> str:
        """
        Save the generated post as a draft in the Pending_Approval folder.

        Args:
            content: Post content to save
            topic: Topic of the post

        Returns:
            Filename of the saved draft
        """
        # Create filename based on topic and timestamp
        topic_clean = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not topic_clean:
            topic_clean = "business_post"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_POST_{timestamp}_{topic_clean}.md"
        filepath = self.pending_approval_path / filename

        # Handle filename conflicts
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            filepath = self.pending_approval_path / f"LINKEDIN_POST_{timestamp}_{topic_clean}_{counter}.md"
            counter += 1

        # Create markdown content
        md_content = f"""# LinkedIn Post Draft: {topic}

## Content
{content}

## Details
- **Topic**: {topic}
- **Generated on**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Pending Approval

## Action Required
Review this post and move to Approved folder to publish to LinkedIn.
"""

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Saved LinkedIn post draft: {filepath.name}")

        # Log the action
        self._log_action("POST_DRAFT_CREATED", f"Created LinkedIn post draft: {filepath.name}")

        return filepath.name

    def check_daily_post_limit(self) -> bool:
        """
        Check if the daily post limit has been reached.

        Returns:
            True if under limit, False if limit reached
        """
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        if not log_file.exists():
            return True

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

            # Count LinkedIn posts made today
            posts_today = 0
            for log in logs:
                if log.get('action') == 'LINKEDIN_POSTED':
                    posts_today += 1

            return posts_today < self.max_posts_per_day

        except (json.JSONDecodeError, KeyError):
            return True

    def post_to_linkedin(self, content: str) -> bool:
        """
        Post content to LinkedIn.

        Args:
            content: Content to post

        Returns:
            True if successful, False otherwise
        """
        if not self.check_daily_post_limit():
            print(f"Daily post limit ({self.max_posts_per_day}) reached. Cannot post to LinkedIn.")
            self._log_action("POST_LIMIT_EXCEEDED", f"Daily post limit ({self.max_posts_per_day}) reached")
            return False

        headers = get_authenticated_headers()
        if not headers:
            print("Error: Could not authenticate with LinkedIn API")
            return False

        # For the IMAP approach, we're not posting directly to LinkedIn via API
        # Instead, we're saving the post as a draft file that the user can manually post

        # Create a filename for the LinkedIn post draft
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"LINKEDIN_READY_TO_POST_{timestamp}.txt"
        filepath = self.done_path / filename

        # Handle filename conflicts
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            filepath = self.done_path / f"LINKEDIN_READY_TO_POST_{timestamp}_{counter}.txt"
            counter += 1

        # Save the post content to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"LinkedIn Post - Ready to Publish\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"===============================\n\n")
            f.write(content)

        print(f"LinkedIn post saved as draft: {filepath.name}")
        print("Please manually copy and paste this content to LinkedIn to publish.")
        self._log_action("LINKEDIN_SAVED_AS_DRAFT", f"LinkedIn post saved as draft: {filepath.name}")
        return True

    def process_approved_post(self, file_path: Path) -> bool:
        """
        Process an approved LinkedIn post file and handle it appropriately.
        For the IMAP approach, this just acknowledges the approval.

        Args:
            file_path: Path to the approved post file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"LinkedIn post approved: {file_path.name}")
            print("This post has been approved and is ready for manual posting to LinkedIn.")

            # In the file-based approach, the user manually copies the content to LinkedIn
            self._log_action("LINKEDIN_APPROVED", f"LinkedIn post approved for manual posting: {file_path.name}")
            return True

        except Exception as e:
            print(f"Error processing approved post {file_path.name}: {e}")
            self._log_action("POST_PROCESS_ERROR", f"Error processing approved post {file_path.name}: {e}")
            return False

    def generate_weekly_post(self, topic: Optional[str] = None) -> str:
        """
        Generate a weekly LinkedIn post based on trending topics in the user's industry.

        Args:
            topic: Specific topic to focus on (optional)

        Returns:
            Filename of the saved draft
        """
        if not topic:
            # Generate a post about trending business topics
            topic = "Weekly Business Insights"

        print(f"Generating LinkedIn post about: {topic}")
        content = self.generate_post_content(topic)
        filename = self.save_post_draft(content, topic)

        return filename

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "processor": "LinkedIn Poster"
        }

        # Create log filename based on today's date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        # Read existing log entries or initialize empty list
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write updated logs back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)


def main():
    """Main function to run the LinkedIn poster."""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    poster = LinkedInPoster(vault_path)

    # Generate a sample weekly post
    topic = "AI Trends in Business"
    filename = poster.generate_weekly_post(topic)
    print(f"Generated LinkedIn post draft: {filename}")


if __name__ == "__main__":
    main()
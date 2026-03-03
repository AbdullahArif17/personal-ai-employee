"""
LinkedIn Generator for the Personal AI Employee system.
Generates professional LinkedIn posts using Gemini AI based on business context.
"""
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()


class LinkedInGenerator:
    """LinkedIn post generator implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "D:/giaic/personal-ai-employee/AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.logs_path = self.vault_path / "Logs"
        self.company_handbook_path = self.vault_path / "Company_Handbook.md"

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file")

        self.client = genai.Client(api_key=api_key)

        # Create directories if they don't exist
        self.pending_approval_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def get_business_context(self) -> str:
        """
        Read business context from Company_Handbook.md.

        Returns:
            Business context as a string
        """
        try:
            with open(self.company_handbook_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️  Company handbook not found at: {self.company_handbook_path}")
            print("Using default business context...")
            return """
# Company Handbook

## Business Focus
Our company specializes in innovative technology solutions, helping businesses grow through strategic digital transformation.

## Values
- Innovation
- Excellence
- Customer-centricity
- Integrity

## Target Audience
Business leaders, entrepreneurs, and professionals interested in technology trends and business growth strategies.
"""
        except Exception as e:
            print(f"⚠️  Error reading company handbook: {e}")
            return "Default business context for generating LinkedIn posts."

    def generate_linkedin_post(self) -> str:
        """
        Generate a professional LinkedIn post using Gemini AI.

        Returns:
            Generated LinkedIn post content
        """
        business_context = self.get_business_context()

        prompt = f"""
Based on the following business context, generate a professional LinkedIn post:

{business_context}

The post should include:
- Business tips or insights
- Information about weekly achievements (if any)
- Industry insights
- A call to action

The post should be engaging, professional, and approximately 300-500 words.
Focus on providing value to the reader and encouraging engagement.
"""

        try:
            response = self.client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt
            )
            return response.text if response.text else "No content generated"
        except Exception as e:
            print(f"❌ Error generating LinkedIn post with Gemini: {e}")
            return "Sample LinkedIn post content - failed to generate with AI."

    def save_post_draft(self, content: str) -> str:
        """
        Save the generated post as a draft in the Pending_Approval folder.

        Args:
            content: LinkedIn post content to save

        Returns:
            Filename of the saved draft
        """
        # Create filename with current date
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"LINKEDIN_post_{date_str}.md"
        filepath = self.pending_approval_path / filename

        # Handle filename conflicts
        counter = 1
        original_filepath = filepath
        while filepath.exists():
            filepath = self.pending_approval_path / f"LINKEDIN_post_{date_str}_{counter}.md"
            counter += 1

        # Create markdown content with YAML header
        yaml_header = f"""---
action: linkedin_post
generated: {datetime.now().strftime('%Y-%m-%d')}
status: pending_approval
---

{content}"""

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(yaml_header)

        print(f"📄 Saved LinkedIn post draft: {filepath.name}")

        # Log the action
        self._log_action("LINKEDIN_DRAFT_CREATED", f"Created LinkedIn post draft: {filepath.name}")

        return filepath.name

    def generate_and_save_post(self) -> str:
        """
        Generate a LinkedIn post and save it as a draft.

        Returns:
            Filename of the saved draft
        """
        print("🔄 Generating LinkedIn post...")

        # Generate the post content
        content = self.generate_linkedin_post()

        # Print the generated post to console
        print("\n" + "="*60)
        print("LinkedIn Post Generated:")
        print("="*60)
        print(content)
        print("="*60 + "\n")

        # Save the post draft
        filename = self.save_post_draft(content)

        print(f"✅ LinkedIn post draft saved to: {self.pending_approval_path / filename}")
        print("📋 Remember: The post requires human approval before posting to LinkedIn.")

        return filename

    def _log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "processor": "LinkedIn Generator"
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
    """Main function to run the LinkedIn generator."""
    print("🚀 Starting LinkedIn Post Generator")
    print("📋 This will generate a LinkedIn post draft for human approval")
    print("-" * 60)

    vault_path = os.getenv('VAULT_PATH', 'D:/giaic/personal-ai-employee/AI_Employee_Vault')

    generator = LinkedInGenerator(vault_path)

    # Generate and save a LinkedIn post
    filename = generator.generate_and_save_post()
    print(f"🎯 LinkedIn post generation completed: {filename}")


if __name__ == "__main__":
    main()
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import os
import yaml
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    logger.warning("Google GenAI library not installed. Using mock implementation.")

def load_api_key():
    """Load API key from environment variables."""
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("No API key found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    return api_key

def load_business_context():
    """Load business context from Company Handbook."""
    handbook_path = "AI_Employee_Vault/Company_Handbook.md"
    if os.path.exists(handbook_path):
        with open(handbook_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        logger.warning(f"Business handbook not found at {handbook_path}")
        return ""

def generate_facebook_post(api_key, business_context, prompt):
    """Generate a professional Facebook post."""
    if not HAS_GENAI:
        # Mock implementation when Google GenAI is not available
        return f"Professional Facebook post content generated from prompt: {prompt}\n\nCall to action: Learn more about our services today!"

    full_prompt = f"""
    Business Context:
    {business_context}

    Based on the above business context, please generate a professional Facebook post with the following requirements:
    - Professional tone
    - 150-300 words
    - Include a clear call to action
    - No hashtag limit
    - Make it engaging and informative

    Here's the specific request: {prompt}
    """

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=full_prompt
    )

    return response.text.strip()

def generate_instagram_post(api_key, business_context, prompt):
    """Generate a casual Instagram post."""
    if not HAS_GENAI:
        # Mock implementation when Google GenAI is not available
        return f"Fun and engaging Instagram post! 🌟 {prompt}\n\n#fun #business #innovation #success #motivation #entrepreneur #growth #teamwork #vision #opportunity #leadership #inspiration #community #goals #progress"

    full_prompt = f"""
    Business Context:
    {business_context}

    Based on the above business context, please generate a casual and engaging Instagram post with the following requirements:
    - Casual, engaging tone
    - Under 150 words
    - Include 10-15 relevant hashtags
    - Include 3-5 emojis
    - Make it fun and attention-grabbing

    Here's the specific request: {prompt}
    """

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=full_prompt
    )

    return response.text.strip()

def create_yaml_header(action, platform):
    """Create YAML frontmatter for the post."""
    return f"""---
action: {action}
platform: {platform}
generated: {datetime.now().strftime('%Y-%m-%d')}
status: pending_approval
---"""

def save_draft(content, action, platform):
    """Save the draft to the Pending_Approval folder."""
    # Create Pending_Approval directory if it doesn't exist
    approval_dir = "AI_Employee_Vault/Pending_Approval"
    Path(approval_dir).mkdir(parents=True, exist_ok=True)

    # Generate filename with current date
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{platform.upper()}_post_{date_str}.md"
    filepath = os.path.join(approval_dir, filename)

    # Create full content with YAML header
    yaml_header = create_yaml_header(action, platform)
    full_content = f"{yaml_header}\n\n{content}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)

    logger.info(f"Draft saved to {filepath}")
    return filepath

def create_facebook_post(prompt):
    """Create a Facebook post draft."""
    api_key = load_api_key()
    business_context = load_business_context()

    content = generate_facebook_post(api_key, business_context, prompt)
    filepath = save_draft(content, "post_facebook", "facebook")

    logger.info(f"Facebook post draft created: {filepath}")
    return filepath

def create_instagram_post(prompt):
    """Create an Instagram post draft."""
    api_key = load_api_key()
    business_context = load_business_context()

    content = generate_instagram_post(api_key, business_context, prompt)
    filepath = save_draft(content, "post_instagram", "instagram")

    logger.info(f"Instagram post draft created: {filepath}")
    return filepath

def main():
    if len(sys.argv) < 2:
        print("Usage: python social_media_poster.py '<prompt>'")
        sys.exit(1)

    prompt = sys.argv[1]

    try:
        # Create both types of posts
        facebook_path = create_facebook_post(prompt)
        instagram_path = create_instagram_post(prompt)

        print("Social media drafts created successfully and placed in Pending_Approval folder")

    except Exception as e:
        logger.error(f"Error creating social media posts: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
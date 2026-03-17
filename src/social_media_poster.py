import sys
import os
<<<<<<< HEAD
from datetime import datetime
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_social_media_posts(topic):
    """Generate Facebook and Instagram posts using Gemini AI."""

    # Get API key from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not gemini_api_key:
        print("ERROR: GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
        return False

    # Read business context from company handbook
    handbook_path = Path(__file__).parent.parent / "AI_Employee_Vault" / "Company_Handbook.md"
    business_context = ""
    if handbook_path.exists():
        with open(handbook_path, 'r', encoding='utf-8') as f:
            business_context = f.read()
    else:
        print("WARNING: Company_Handbook.md not found, proceeding without business context")

    # Import Google Generative AI
    try:
        import google.generativeai as genai
    except ImportError:
        print("ERROR: google-generativeai package not installed. Please install with: pip install google-generativeai")
        return False

    # Configure the API key
    genai.configure(api_key=gemini_api_key)

    # Get the model
    model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

    # Current date for filenames
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_filename = datetime.now().strftime("%Y%m%d")

    # Define the prompt for Facebook post
    facebook_prompt = f"""
    Business Context: {business_context}

    Topic: {topic}

    Create a professional Facebook post about the given topic. The post should be:
    - Professional and engaging tone
    - 150-300 words in length
    - Include a compelling call to action
    - Suitable for business promotion
    - Include relevant details about benefits or value proposition

    Do not include hashtags in the Facebook post.
    """

    # Define the prompt for Instagram post
    instagram_prompt = f"""
    Business Context: {business_context}

    Topic: {topic}

    Create a casual and engaging Instagram post about the given topic. The post should be:
    - Casual and friendly tone
    - Under 150 words in length
    - Include 10-15 relevant hashtags
    - Include appropriate emojis
    - Have a strong hook to grab attention
    - Include a call to action

    Format the post with emojis and make it visually appealing for Instagram.
    """

    try:
        # Generate Facebook post
        print("Generating Facebook post...")
        facebook_response = model.generate_content(facebook_prompt)
        facebook_content = facebook_response.text.strip()

        # Generate Instagram post
        print("Generating Instagram post...")
        instagram_response = model.generate_content(instagram_prompt)
        instagram_content = instagram_response.text.strip()

        # Create the Pending_Approval directory if it doesn't exist
        pending_approval_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Pending_Approval"
        pending_approval_dir.mkdir(parents=True, exist_ok=True)

        # Create Facebook post file with YAML frontmatter
        facebook_filename = f"FACEBOOK_post_{current_date_filename}.md"
        facebook_filepath = pending_approval_dir / facebook_filename

        facebook_file_content = f"""---
action: post_facebook
platform: facebook
generated: {current_date}
status: pending_approval
---

{facebook_content}"""

        with open(facebook_filepath, 'w', encoding='utf-8') as f:
            f.write(facebook_file_content)

        # Create Instagram post file with YAML frontmatter
        instagram_filename = f"INSTAGRAM_post_{current_date_filename}.md"
        instagram_filepath = pending_approval_dir / instagram_filename

        instagram_file_content = f"""---
action: post_instagram
platform: instagram
generated: {current_date}
status: pending_approval
---

{instagram_content}"""

        with open(instagram_filepath, 'w', encoding='utf-8') as f:
            f.write(instagram_file_content)

        print(f"Social media drafts created successfully and placed in Pending_Approval folder")
        print(f"- {facebook_filename}")
        print(f"- {instagram_filename}")

        # Log the action
        logs_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Logs"
        logs_dir.mkdir(exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "SOCIAL_MEDIA_DRAFT_CREATED",
            "facebook_file": str(facebook_filepath),
            "instagram_file": str(instagram_filepath),
            "topic": topic
        }

        # Append to the daily log file
        today_log = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        logs = []
        if today_log.exists():
            with open(today_log, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    logs = []

        logs.append(log_entry)

        with open(today_log, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

        return True

    except Exception as e:
        print(f"ERROR: Failed to generate social media posts: {e}")
        return False


if __name__ == "__main__":
    # Get topic from command line argument or use default
    topic = sys.argv[1] if len(sys.argv) > 1 else "our AI automation services"

    success = generate_social_media_posts(topic)

    if not success:
        sys.exit(1)
=======
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
>>>>>>> 561c08169a1dcfd3d92b53e2b7406218863ced50

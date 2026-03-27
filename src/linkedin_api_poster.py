import os
import sys
import requests
from datetime import datetime
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_linkedin_posts(topic=None):
    """Generate LinkedIn posts using Gemini AI."""

    # Get API keys from environment
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

    # Determine the topic
    if not topic:
        topic = "our AI automation services"

    # Define the prompt for professional article post
    article_prompt = f"""
    Business Context: {business_context}

    Topic: {topic}

    Create a professional LinkedIn article about the given topic. The post should be:
    - Professional and insightful tone
    - 300-500 words in length
    - Include valuable insights and practical advice
    - Engaging introduction and conclusion
    - Structured with clear paragraphs
    - Include a call to action at the end
    - Suitable for business professionals and decision makers

    Format as a professional LinkedIn article.
    """

    # Define the prompt for short insight post
    insight_prompt = f"""
    Business Context: {business_context}

    Topic: {topic}

    Create a short LinkedIn insight about the given topic. The post should be:
    - Professional and concise tone
    - 150 words maximum
    - Include key insights and practical takeaways
    - Clear and impactful message
    - Suitable for business professionals and decision makers
    - Include a call to action

    Format as a short LinkedIn insight.
    """

    try:
        # Generate article post
        print("Generating LinkedIn article post...")
        article_response = model.generate_content(article_prompt)
        article_content = article_response.text.strip()

        # Generate insight post
        print("Generating LinkedIn insight post...")
        insight_response = model.generate_content(insight_prompt)
        insight_content = insight_response.text.strip()

        # Create the Pending_Approval directory if it doesn't exist
        pending_approval_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Pending_Approval"
        pending_approval_dir.mkdir(parents=True, exist_ok=True)

        # Create article post file with YAML frontmatter
        article_filename = f"LINKEDIN_article_{current_date_filename}.md"
        article_filepath = pending_approval_dir / article_filename

        article_file_content = f"""---
action: post_linkedin
type: article
generated: {current_date}
status: pending_approval
---

{article_content}"""

        with open(article_filepath, 'w', encoding='utf-8') as f:
            f.write(article_file_content)

        # Create insight post file with YAML frontmatter
        insight_filename = f"LINKEDIN_insight_{current_date_filename}.md"
        insight_filepath = pending_approval_dir / insight_filename

        insight_file_content = f"""---
action: post_linkedin
type: insight
generated: {current_date}
status: pending_approval
---

{insight_content}"""

        with open(insight_filepath, 'w', encoding='utf-8') as f:
            f.write(insight_file_content)

        print(f"LinkedIn drafts created successfully and placed in Pending_Approval folder")
        print(f"- {article_filename}")
        print(f"- {insight_filename}")

        # Log the action
        logs_dir = Path(__file__).parent.parent / "AI_Employee_Vault" / "Logs"
        logs_dir.mkdir(exist_ok=True)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "LINKEDIN_DRAFT_CREATED",
            "article_file": str(article_filepath),
            "insight_file": str(insight_filepath),
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
        print(f"ERROR: Failed to generate LinkedIn posts: {e}")
        return False


def post_to_linkedin(content):
    """Post content to LinkedIn using the official API."""
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if not access_token:
        print("ERROR: LINKEDIN_ACCESS_TOKEN not found in environment variables")
        return False

    try:
        # Get user ID
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(
            'https://api.linkedin.com/v2/userinfo',
            headers=headers
        )

        if user_response.status_code != 200:
            print(f"ERROR: Failed to get user info: {user_response.json()}")
            return False

        user_id = user_response.json().get('sub')

        if not user_id:
            print("ERROR: Could not retrieve user ID from LinkedIn API")
            return False

        # Post to LinkedIn
        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(
            'https://api.linkedin.com/v2/ugcPosts',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            },
            json=post_data
        )

        if response.status_code == 201:
            print(f"SUCCESS: Posted to LinkedIn!")
            return True
        else:
            print(f"ERROR: {response.json()}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to post to LinkedIn: {e}")
        return False


def main():
    """Main function to run the LinkedIn poster."""
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else None

    success = generate_linkedin_posts(topic)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
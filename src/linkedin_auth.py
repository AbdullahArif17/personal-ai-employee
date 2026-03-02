"""
LinkedIn authentication module for the Personal AI Employee system.
Handles authentication for LinkedIn API access.
"""
import os
import requests
from typing import Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_linkedin_access_token() -> Optional[str]:
    """
    Get LinkedIn access token from environment variable.

    Returns:
        Access token string if available, None otherwise
    """
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

    if not access_token:
        print("Error: LinkedIn access token not found in environment variables.")
        print("Please set LINKEDIN_ACCESS_TOKEN in your .env file.")
        return None

    return access_token


def validate_linkedin_token(access_token: str) -> bool:
    """
    Validate the LinkedIn access token by making a test request.

    Args:
        access_token: LinkedIn access token to validate

    Returns:
        True if token is valid, False otherwise
    """
    if not access_token:
        return False

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        # Test request to get basic profile information
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers,
            timeout=10
        )

        return response.status_code == 200

    except requests.RequestException as e:
        print(f"Error validating LinkedIn token: {e}")
        return False


def get_authenticated_headers() -> Optional[dict]:
    """
    Get authenticated headers for LinkedIn API requests.

    Returns:
        Dictionary with authentication headers if valid, None otherwise
    """
    access_token = get_linkedin_access_token()

    if not access_token:
        return None

    if not validate_linkedin_token(access_token):
        print("Error: LinkedIn access token is not valid.")
        return None

    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }


def refresh_linkedin_token_if_needed():
    """
    LinkedIn tokens are typically long-lived, but if refresh is needed,
    this would handle it. Currently just validates the existing token.
    """
    access_token = get_linkedin_access_token()
    if not access_token:
        return False

    return validate_linkedin_token(access_token)


def get_current_user_profile() -> Optional[dict]:
    """
    Get the current user's LinkedIn profile information.

    Returns:
        Profile information dictionary if successful, None otherwise
    """
    headers = get_authenticated_headers()
    if not headers:
        return None

    try:
        response = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting profile: {response.status_code} - {response.text}")
            return None

    except requests.RequestException as e:
        print(f"Error getting LinkedIn profile: {e}")
        return None


def get_current_user_email() -> Optional[str]:
    """
    Get the current user's email address from LinkedIn.

    Returns:
        Email address string if successful, None otherwise
    """
    headers = get_authenticated_headers()
    if not headers:
        return None

    try:
        response = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            elements = data.get('elements', [])
            if elements:
                email_handle = elements[0].get('handle~', {})
                return email_handle.get('emailAddress')

        return None

    except requests.RequestException as e:
        print(f"Error getting LinkedIn email: {e}")
        return None


if __name__ == '__main__':
    # Test the authentication
    token = get_linkedin_access_token()
    if token:
        print("LinkedIn access token found")
        if validate_linkedin_token(token):
            print("Token validation successful")

            profile = get_current_user_profile()
            if profile:
                print(f"Profile retrieved: {profile.get('localizedFirstName', 'Unknown')} {profile.get('localizedLastName', 'Unknown')}")
        else:
            print("Token validation failed")
    else:
        print("No LinkedIn access token found")
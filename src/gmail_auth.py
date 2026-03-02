"""
Gmail authentication module for the Personal AI Employee system.
Handles OAuth2 authentication for Gmail API access.
"""
import os
import pickle
from typing import Optional

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Load environment variables
load_dotenv()

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail() -> Optional[Credentials]:
    """
    Authenticate with Gmail API using OAuth2.

    Returns:
        Credentials object if authentication is successful, None otherwise
    """
    creds = None

    # Token file stores the user's access and refresh tokens
    token_file = 'token.pickle'

    # Check if token file exists and load credentials
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                # If refresh fails, remove the token file and restart authentication
                if os.path.exists(token_file):
                    os.remove(token_file)

        # If credentials are still not valid, initiate the OAuth flow
        if not creds or not creds.valid:
            creds = _perform_oauth_flow()

            # Save the credentials for the next run
            if creds:
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

    return creds


def _perform_oauth_flow() -> Optional[Credentials]:
    """
    Perform the OAuth2 flow to get new credentials.

    Returns:
        Credentials object if successful, None otherwise
    """
    # Get credentials from environment variables
    client_id = os.getenv('GMAIL_CLIENT_ID')
    client_secret = os.getenv('GMAIL_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("Error: Gmail credentials not found in environment variables.")
        print("Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in your .env file.")
        return None

    # Create a temporary client_secrets dictionary
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    try:
        # Create flow instance
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        flow.run_local_server(port=0)

        return flow.credentials
    except Exception as e:
        print(f"Error during OAuth flow: {e}")
        return None


def get_authenticated_service():
    """
    Get an authenticated Gmail API service instance.

    Returns:
        Gmail service object if authentication is successful, None otherwise
    """
    try:
        from googleapiclient.discovery import build

        creds = authenticate_gmail()
        if creds:
            service = build('gmail', 'v1', credentials=creds)
            return service
        else:
            return None
    except ImportError:
        print("Error: google-api-python-client library is not installed.")
        print("Please install it using: pip install google-api-python-client")
        return None
    except Exception as e:
        print(f"Error creating Gmail service: {e}")
        return None


def refresh_credentials_if_needed(creds: Credentials) -> Credentials:
    """
    Refresh credentials if they are expired.

    Args:
        creds: Current credentials object

    Returns:
        Updated credentials object
    """
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            return None

    return creds


if __name__ == '__main__':
    # Test the authentication
    credentials = authenticate_gmail()
    if credentials:
        print("Gmail authentication successful!")
    else:
        print("Gmail authentication failed!")
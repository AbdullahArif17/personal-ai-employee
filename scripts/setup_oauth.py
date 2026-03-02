"""
OAuth Setup Script for Personal AI Employee Silver Tier

This script helps set up OAuth credentials for Gmail and LinkedIn APIs.
"""
import os
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scope
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def setup_gmail_oauth():
    """Guide the user through Gmail OAuth setup."""
    print("Setting up Gmail OAuth...")
    print("Before proceeding, you need to create a Google Cloud Project and enable the Gmail API:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com")
    print("4. Create credentials (OAuth 2.0 Client IDs) for a Desktop application")
    print("5. Download the credentials JSON file")
    print()

    client_creds_path = input("Enter the path to your downloaded credentials JSON file: ").strip()

    if not os.path.exists(client_creds_path):
        print(f"Error: File {client_creds_path} does not exist.")
        return False

    # Load client credentials
    with open(client_creds_path, 'r') as f:
        client_config = eval(f.read())  # In production, use json.load instead

    # Create flow instance
    flow = InstalledAppFlow.from_client_config(client_config['web'], GMAIL_SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    token_file = 'token.pickle'
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)

    print(f"Gmail OAuth setup completed! Token saved to {token_file}")
    print("Your Gmail access is now set up for the Personal AI Employee system.")
    return True


def setup_linkedin_oauth():
    """Guide the user through LinkedIn OAuth setup."""
    print("Setting up LinkedIn OAuth...")
    print("Before proceeding, you need to create a LinkedIn App:")
    print("1. Go to: https://www.linkedin.com/developers/")
    print("2. Create a new app")
    print("3. Note down your Client ID and Client Secret")
    print("4. Set the redirect URL to: https://www.linkedin.com/developers/tools/oauth/redirect")
    print()

    client_id = input("Enter your LinkedIn Client ID: ").strip()
    client_secret = input("Enter your LinkedIn Client Secret: ").strip()

    print()
    print("To get your access token:")
    print("1. Go to: https://www.linkedin.com/developers/tools/oauth/redirect")
    print("2. Enter your Client ID and Client Secret")
    print("3. Click 'Request Access Token'")
    print("4. Copy the access token")
    print()

    access_token = input("Enter your LinkedIn Access Token: ").strip()

    print()
    print("LinkedIn OAuth setup completed!")
    print("Add the following to your .env file:")
    print(f"LINKEDIN_CLIENT_ID={client_id}")
    print(f"LINKEDIN_CLIENT_SECRET={client_secret}")
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print()
    print("Or add them to your system environment variables.")

    return True


def main():
    """Main function to run the OAuth setup."""
    print("Personal AI Employee - OAuth Setup")
    print("==================================")
    print()
    print("This script will help you set up OAuth credentials for Silver tier features.")
    print()

    while True:
        print("Choose which service to set up:")
        print("1. Gmail")
        print("2. LinkedIn")
        print("3. Both")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == "1":
            setup_gmail_oauth()
            break
        elif choice == "2":
            setup_linkedin_oauth()
            break
        elif choice == "3":
            setup_gmail_oauth()
            print()
            setup_linkedin_oauth()
            break
        elif choice == "4":
            print("Exiting OAuth setup.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
            print()


if __name__ == "__main__":
    main()
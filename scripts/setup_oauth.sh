#!/bin/bash

# OAuth Setup Script for Personal AI Employee Silver Tier

echo "Personal AI Employee - OAuth Setup"
echo "=================================="
echo
echo "This script will guide you through setting up OAuth credentials for Silver tier features."
echo

# Function to setup Gmail OAuth
setup_gmail_oauth() {
    echo "Setting up Gmail OAuth..."
    echo "Before proceeding, you need to create a Google Cloud Project and enable the Gmail API:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a new project or select an existing one"
    echo "3. Enable the Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com"
    echo "4. Create credentials (OAuth 2.0 Client IDs) for a Desktop application"
    echo "5. Download the credentials JSON file"
    echo

    read -p "Enter the path to your downloaded credentials JSON file: " client_creds_path

    if [ ! -f "$client_creds_path" ]; then
        echo "Error: File $client_creds_path does not exist."
        return 1
    fi

    echo
    echo "Running Gmail OAuth setup..."
    echo "Please run: python scripts/setup_oauth.py"
    echo "And select option 1 for Gmail setup."
    echo
}

# Function to setup LinkedIn OAuth
setup_linkedin_oauth() {
    echo "Setting up LinkedIn OAuth..."
    echo "Before proceeding, you need to create a LinkedIn App:"
    echo "1. Go to: https://www.linkedin.com/developers/"
    echo "2. Create a new app"
    echo "3. Note down your Client ID and Client Secret"
    echo "4. Set the redirect URL to: https://www.linkedin.com/developers/tools/oauth/redirect"
    echo

    read -p "Enter your LinkedIn Client ID: " client_id
    read -p "Enter your LinkedIn Client Secret: " client_secret

    echo
    echo "To get your access token:"
    echo "1. Go to: https://www.linkedin.com/developers/tools/oauth/redirect"
    echo "2. Enter your Client ID and Client Secret"
    echo "3. Click 'Request Access Token'"
    echo "4. Copy the access token"
    echo

    read -p "Enter your LinkedIn Access Token: " access_token

    echo
    echo "LinkedIn OAuth setup completed!"
    echo "Add the following to your .env file:"
    echo "LINKEDIN_CLIENT_ID=$client_id"
    echo "LINKEDIN_CLIENT_SECRET=$client_secret"
    echo "LINKEDIN_ACCESS_TOKEN=$access_token"
    echo
    echo "Or add them to your system environment variables."
    echo
}

# Main menu
while true; do
    echo "Choose which service to set up:"
    echo "1. Gmail"
    echo "2. LinkedIn"
    echo "3. Both"
    echo "4. Exit"
    read -p "Enter your choice (1-4): " choice

    case $choice in
        1)
            setup_gmail_oauth
            break
            ;;
        2)
            setup_linkedin_oauth
            break
            ;;
        3)
            setup_gmail_oauth
            echo
            setup_linkedin_oauth
            break
            ;;
        4)
            echo "Exiting OAuth setup."
            exit 0
            ;;
        *)
            echo "Invalid choice. Please enter 1, 2, 3, or 4."
            echo
            ;;
    esac
done

echo
echo "OAuth setup completed!"
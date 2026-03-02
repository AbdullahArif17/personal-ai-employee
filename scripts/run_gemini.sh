#!/bin/bash

# Personal AI Employee - Gemini API Integration Script
# This script processes files in the Needs_Action folder using the Google Gemini API

set -e  # Exit on any error

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Configuration
VAULT_PATH="${VAULT_PATH:-./AI_Employee_Vault}"
NEEDS_ACTION_DIR="$VAULT_PATH/Needs_Action"
DONE_DIR="$VAULT_PATH/Done"
PENDING_APPROVAL_DIR="$VAULT_PATH/Pending_Approval"
APPROVED_DIR="$VAULT_PATH/Approved"
LOGS_DIR="$VAULT_PATH/Logs"
SKILLS_DIR="$VAULT_PATH/skills"

# DRY_RUN mode - set to "true" to run without making actual changes
DRY_RUN="${DRY_RUN:-false}"

# Timestamp for log entries
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Function to log actions
log_action() {
    local action_type="$1"
    local message="$2"

    # Create log entry
    local log_entry="{\"timestamp\": \"$TIMESTAMP\", \"action\": \"$action_type\", \"message\": \"$message\", \"processor\": \"Gemini\"}"

    if [ "$DRY_RUN" = "true" ]; then
        echo "(DRY RUN) Would log: $log_entry"
    else
        # Create logs directory if it doesn't exist
        mkdir -p "$LOGS_DIR"

        # Create log filename based on today's date
        local today=$(date +"%Y-%m-%d")
        local log_file="$LOGS_DIR/$today.json"

        # Initialize log file if it doesn't exist
        if [ ! -f "$log_file" ]; then
            echo "[]" > "$log_file"
        fi

        # Read existing logs and append new entry
        local existing_logs=$(cat "$log_file")
        local updated_logs=$(echo "$existing_logs" | jq --argjson new_log "$log_entry" '. + [$new_log]' 2>/dev/null || echo "[]")
        if [ "$updated_logs" != "[]" ]; then
            echo "$updated_logs" > "$log_file"
        else
            # Fallback if jq is not available
            local temp_logs=$(mktemp)
            echo "[" > "$temp_logs"
            cat "$log_file" | grep -v "^\\[$" | grep -v "^\\]$" | sed '$d' | sed '/./,$!d' >> "$temp_logs"
            if [ -s "$temp_logs" ]; then
                echo "," >> "$temp_logs"
            fi
            echo "$log_entry" >> "$temp_logs"
            echo "]" >> "$temp_logs"
            mv "$temp_logs" "$log_file"
        fi
    fi
}

# Function to update dashboard
update_dashboard() {
    if [ "$DRY_RUN" = "true" ]; then
        echo "(DRY RUN) Would update dashboard"
        log_action "DASHBOARD_UPDATE" "Dashboard update skipped (DRY_RUN mode)"
    else
        # Run the dashboard update Python script
        if command -v python3 &> /dev/null; then
            python3 -m src.dashboard_updater
            log_action "DASHBOARD_UPDATE" "Dashboard updated successfully"
        elif command -v python &> /dev/null; then
            python -m src.dashboard_updater
            log_action "DASHBOARD_UPDATE" "Dashboard updated successfully"
        else
            log_action "ERROR" "Python not found, cannot update dashboard"
        fi
    fi
}

# Main execution
echo "Starting Gemini API integration script..."
echo "Vault path: $VAULT_PATH"
echo "Dry run mode: $DRY_RUN"
echo "Timestamp: $TIMESTAMP"

# Check if Needs_Action directory exists
if [ ! -d "$NEEDS_ACTION_DIR" ]; then
    echo "Error: Needs_Action directory does not exist: $NEEDS_ACTION_DIR"
    log_action "ERROR" "Needs_Action directory does not exist: $NEEDS_ACTION_DIR"
    exit 1
fi

# Find all files in Needs_Action directory
file_count=$(find "$NEEDS_ACTION_DIR" -maxdepth 1 -type f -not -name ".*" | wc -l)

if [ "$file_count" -eq 0 ]; then
    echo "No files to process in $NEEDS_ACTION_DIR"
    log_action "NO_FILES" "No files found to process in Needs_Action directory"
else
    echo "Found $file_count file(s) to process"
    log_action "PROCESS_START" "Found $file_count file(s) to process in Needs_Action"

    # Run the Gemini processor Python script
    if [ "$DRY_RUN" = "true" ]; then
        echo "(DRY RUN) Would run Gemini processor"
    else
        if command -v python3 &> /dev/null; then
            python3 -m src.gemini_processor
            log_action "PROCESS_COMPLETE" "Completed processing files with Gemini API"
        elif command -v python &> /dev/null; then
            python -m src.gemini_processor
            log_action "PROCESS_COMPLETE" "Completed processing files with Gemini API"
        else
            log_action "ERROR" "Python not found, cannot run Gemini processor"
            exit 1
        fi
    fi
fi

# Update the dashboard
update_dashboard

echo "Gemini API integration script completed."

# If not in dry run mode, update the dashboard one more time with system status
if [ "$DRY_RUN" != "true" ]; then
    # Update dashboard with system status
    if command -v python3 &> /dev/null; then
        python3 -c "
import sys
sys.path.insert(0, '.')
from src.dashboard_updater import DashboardUpdater
import os
vault_path = os.environ.get('VAULT_PATH', './AI_Employee_Vault')
updater = DashboardUpdater(vault_path)
# Update system status
with open('$VAULT_PATH/Dashboard.md', 'r') as f:
    content = f.read()
# Replace system status section with updated info
import datetime
status_start = content.find('## System Status')
if status_start != -1:
    status_end = content.find('## ', status_start + 1)
    if status_end == -1:
        status_end = len(content)
    status_section = '''## System Status

- Filesystem watcher: **Inactive**
- Gemini API integration: **Active (just ran)**
- Last run: **$(date +'%Y-%m-%d %H:%M:%S')**
- DRY_RUN mode: **Disabled**
'''
    new_content = content[:status_start] + status_section
    if status_end < len(content):
        new_content += content[status_end:]
    with open('$VAULT_PATH/Dashboard.md', 'w') as f:
        f.write(new_content)
"
    fi
fi
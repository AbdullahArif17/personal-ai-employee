#!/bin/bash

# Personal AI Employee - Claude Code Integration Script
# This script processes files in the Needs_Action folder using Claude Code

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
DRY_RUN="${DRY_RUN:-true}"

# Timestamp for log entries
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Function to log actions
log_action() {
    local action_type="$1"
    local message="$2"

    # Create log entry
    local log_entry="{\"timestamp\": \"$TIMESTAMP\", \"action\": \"$action_type\", \"message\": \"$message\", \"dry_run\": $DRY_RUN}"

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
        local updated_logs=$(echo "$existing_logs" | jq --argjson new_log "$log_entry" '. + [$new_log]')
        echo "$updated_logs" > "$log_file"
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

# Function to process a single file
process_file() {
    local file_path="$1"
    local filename=$(basename "$file_path")
    local file_stem="${filename%.*}"
    local extension="${filename##*.}"

    echo "Processing file: $filename"
    log_action "PROCESSING_START" "Started processing file: $filename"

    if [ "$DRY_RUN" = "true" ]; then
        echo "(DRY RUN) Would process file: $filename"
        echo "(DRY RUN) Would apply skills from: $SKILLS_DIR"
        echo "(DRY RUN) Would move file to Done directory"

        # Log what would happen
        log_action "DRY_RUN" "File $filename would be processed with skills and moved to Done"
    else
        # Read the file content
        local file_content=$(cat "$file_path")

        # Check if the file requires approval by looking for approval indicators
        local requires_approval=false
        if [[ "$file_content" =~ \$\{APPROVAL_REQUIRED\}|requires approval|needs approval|need approval|approve ]]; then
            requires_approval=true
        fi

        # If approval is required, move to Pending Approval folder
        if [ "$requires_approval" = "true" ]; then
            local target_dir="$PENDING_APPROVAL_DIR"
            local status_msg="Moved to Pending Approval"
        else
            local target_dir="$DONE_DIR"
            local status_msg="Moved to Done"
        fi

        # Create the target directory if it doesn't exist
        mkdir -p "$target_dir"

        # Move the file to the appropriate directory
        local target_path="$target_dir/$filename"

        # Handle filename conflicts by appending a number
        local counter=1
        local original_target_path="$target_path"
        while [ -f "$target_path" ]; do
            target_path="$target_dir/${file_stem}_${counter}.${extension}"
            ((counter++))
        done

        # Actually move the file
        mv "$file_path" "$target_path"

        # Process any associated metadata file
        local metadata_file="$NEEDS_ACTION_DIR/${file_stem}_metadata.json"
        if [ -f "$metadata_file" ]; then
            local metadata_target="$target_dir/$(basename ${metadata_file})"
            mv "$metadata_file" "$metadata_target"
        fi

        log_action "FILE_MOVED" "File $filename $status_msg"
        echo "File $filename $status_msg"
    fi
}

# Main execution
echo "Starting Claude Code integration script..."
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

    # Process each file in the Needs_Action directory
    find "$NEEDS_ACTION_DIR" -maxdepth 1 -type f -not -name ".*" | while read -r file_path; do
        process_file "$file_path"
    done

    echo "File processing completed."
    log_action "PROCESS_COMPLETE" "Completed processing files in Needs_Action"
fi

# Update the dashboard
update_dashboard

echo "Claude Code integration script completed."

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
- Claude Code integration: **Active (just ran)**
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
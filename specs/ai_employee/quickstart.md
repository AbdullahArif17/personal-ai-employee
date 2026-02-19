# Quickstart Guide: Personal AI Employee

## Overview

This guide will help you set up and run the Personal AI Employee system in under 10 minutes. The system monitors an Obsidian vault, processes tasks automatically, and maintains structured outputs—all running on your local machine.

## Prerequisites

- Python 3.13 or higher
- uv package manager (recommended) or pip
- Claude Code CLI installed and configured
- Git (optional, for version control)

## Installation

### 1. Clone or Download the Project

```bash
git clone <repository-url>
cd personal-ai-employee
```

Or download and extract the project archive to a local directory.

### 2. Install Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

If no requirements.txt exists, install directly:
```bash
pip install watchdog python-dotenv
```

### 3. Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Edit the `.env` file to match your preferences:
- Set `DRY_RUN=true` for initial testing
- Modify vault paths if needed
- Add any Claude API keys if required

## Initial Setup

### 1. Verify Vault Structure

The system will create the following folder structure in `AI_Employee_Vault/`:
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── skills/
├── Inbox/
├── Needs_Action/
├── Done/
├── Logs/
├── Pending_Approval/
└── Approved/
```

These folders will be created automatically if they don't exist.

### 2. Customize Company Handbook

Review and customize `AI_Employee_Vault/Company_Handbook.md` with your preferences:
- Communication style
- Approval thresholds
- Contact information
- Task handling guidelines

### 3. Configure Skills

The system comes with default skills in `AI_Employee_Vault/skills/`:
- `SKILL_triage.md` - Task categorization
- `SKILL_dashboard_update.md` - Dashboard updates
- `SKILL_response_formatting.md` - Response formatting
- `SKILL_approval_process.md` - Approval workflow

Review these and modify as needed for your use cases.

## Running the System

### 1. Start the Filesystem Watcher

Open a terminal and run:
```bash
python -m src.filesystem_watcher
```

The watcher will monitor the `Inbox/` folder for new files and copy them to `Needs_Action/` with metadata.

### 2. Process Tasks with Claude Code

In a separate terminal, run the Claude integration script:
```bash
bash scripts/run_claude.sh
```

This will process all files in the `Needs_Action/` folder using Claude Code.

### 3. Check the Dashboard

Monitor the system status in `AI_Employee_Vault/Dashboard.md`:
- File counts in each folder
- Recent activity
- System status
- Statistics

## First Task Example

### 1. Create a Test Task

Create a simple text file in `AI_Employee_Vault/Inbox/`:
```bash
echo "Please help me organize my upcoming meetings for next week." > "organize-meetings.txt"
```

### 2. Observe the Process

- The filesystem watcher will detect the file
- It will be copied to `Needs_Action/` with a metadata file
- Run the Claude script to process it
- Check the dashboard for updates

### 3. Verify Processing

- Check `Needs_Action/` for the copied file
- Check `Logs/` for processing entries
- Update your `Dashboard.md` should reflect the new activity

## Configuration Options

### Environment Variables

Key settings in `.env`:
- `DRY_RUN=true/false` - Enable/disable actual changes
- `VAULT_PATH` - Path to the AI Employee vault
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Folder Locations

You can customize folder locations in the `.env` file:
- `INBOX_FOLDER`
- `NEEDS_ACTION_FOLDER`
- `DONE_FOLDER`
- `LOGS_FOLDER`
- `PENDING_APPROVAL_FOLDER`
- `APPROVED_FOLDER`

## Automation Setup

### Running Continuously

To keep the filesystem watcher running continuously:

Using a process manager like PM2:
```bash
npm install -g pm2
pm2 start "python -m src.filesystem_watcher" --name "ai-employee-watcher"
```

### Scheduled Processing

To run Claude processing on a schedule:

On Linux/macOS, add to crontab:
```bash
# Run every 30 minutes
*/30 * * * * cd /path/to/personal-ai-employee && bash scripts/run_claude.sh
```

On Windows, use Task Scheduler with a scheduled task running:
```
cd C:\path\to\personal-ai-employee && bash scripts/run_claude.sh
```

## Troubleshooting

### Common Issues

1. **Filesystem watcher not detecting changes**
   - Check if the `Inbox/` folder exists
   - Verify you have read/write permissions
   - Ensure no other processes are locking the files

2. **Claude integration not working**
   - Verify Claude Code CLI is installed and authenticated
   - Check the Claude skill files for proper instructions
   - Review logs in the `Logs/` folder

3. **Dashboard not updating**
   - Run the dashboard updater manually: `python -m src.dashboard_updater`
   - Check for errors in the log files

### Checking Logs

Review system logs in `AI_Employee_Vault/Logs/`:
- Look for files named `{YYYY-MM-DD}.json`
- Each day's activities are logged in separate files
- Search for ERROR or WARNING entries

## Next Steps

1. **Customize Skills**: Modify the skill files to better handle your specific task types
2. **Adjust Approval Thresholds**: Configure which tasks require human approval
3. **Set Up Automation**: Configure continuous watching and scheduled processing
4. **Extend Functionality**: Add new skills or modify existing ones for your needs
5. **Monitor Performance**: Track system performance and adjust as needed

## Support

- Check the logs in the `Logs/` folder for error details
- Review the dashboard for system status
- Refer to the full documentation for advanced configuration
- Ensure your Claude Code setup is properly configured
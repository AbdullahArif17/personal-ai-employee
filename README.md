# Personal AI Employee

A local automation system where Claude Code acts as an AI employee that monitors an Obsidian markdown vault, processes incoming tasks, and writes structured outputs — all running on the user's local machine.

## Overview

The Personal AI Employee is a Bronze-tier automation system that:
- Monitors an Obsidian vault for incoming tasks
- Processes tasks automatically using Claude Code
- Maintains structured outputs in designated folders
- Runs entirely on your local machine for privacy and security

## Features

1. **Obsidian Vault Structure**: Organized folder system with Inbox, Needs_Action, Done, Logs, Pending_Approval, and Approved folders
2. **Dashboard.md**: Live summary showing pending items, recent activity, and status
3. **Company_Handbook.md**: Rules of engagement for the AI (tone, approval thresholds, contact list)
4. **Filesystem Watcher**: Python script monitoring the Inbox folder and copying new files to Needs_Action with metadata
5. **Agent SKILL.md files**: Markdown skill files Claude Code reads to process tasks
6. **Claude Code Integration**: Automated processing of tasks following skill instructions

## Prerequisites

- Python 3.13+
- Claude Code CLI installed and configured
- Obsidian installed and configured (optional, but recommended)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd personal-ai-employee
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   # or if you don't have uv:
   pip install -r requirements.txt
   ```

3. Copy the example environment file and configure:
   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

## Setup

1. **Configure Environment Variables**
   - Edit the `.env` file with your preferred settings
   - Set `DRY_RUN=true` for development/testing
   - Configure vault paths as needed

2. **Initialize the Vault Structure**
   The system will automatically create the necessary folder structure:
   ```
   AI_Employee_Vault/
   ├── Dashboard.md
   ├── Company_Handbook.md
   ├── skills/
   │   ├── SKILL_triage.md
   │   ├── SKILL_dashboard_update.md
   │   ├── SKILL_response_formatting.md
   │   └── SKILL_approval_process.md
   ├── Inbox/
   ├── Needs_Action/
   ├── Done/
   ├── Logs/
   ├── Pending_Approval/
   └── Approved/
   ```

3. **Configure Claude Code Skills**
   - Customize the skill files in `AI_Employee_Vault/skills/` to define how Claude Code should process different types of tasks
   - Update `Company_Handbook.md` with rules for your AI employee

## Usage

### Running the Filesystem Watcher

The filesystem watcher monitors the Inbox folder and processes new files:

```bash
python -m src.filesystem_watcher
```

To run with PM2 for continuous operation:
```bash
# Install PM2 if not already installed
npm install -g pm2

# Start the filesystem watcher with PM2
pm2 start ecosystem.config.js

# View the status
pm2 status

# Stop the watcher
pm2 stop personal-ai-employee
```

### Processing Tasks with Claude Code

Run the Claude Code processor to handle tasks in the Needs_Action folder:

```bash
bash scripts/run_claude.sh
```

Or schedule it to run periodically using cron (Linux/macOS) or Task Scheduler (Windows).

### Scheduling Claude Processing

To run Claude processing on a schedule:

On Linux/macOS, add to crontab (`crontab -e`):
```bash
# Run every 30 minutes
*/30 * * * * cd /path/to/personal-ai-employee && bash scripts/run_claude.sh >> /tmp/claude-processing.log 2>&1

# Run every hour
0 * * * * cd /path/to/personal-ai-employee && bash scripts/run_claude.sh
```

On Windows, use Task Scheduler with a scheduled task running:
```
cd C:\path\to\personal-ai-employee && bash scripts/run_claude.sh
```

### Manual Operation

1. Place a task file in the `AI_Employee_Vault/Inbox/` folder
2. The watcher will copy it to `AI_Employee_Vault/Needs_Action/` with metadata
3. Run Claude Code to process the task
4. The processed task will be moved to `AI_Employee_Vault/Done/`
5. Dashboard.md will be updated with the latest status

## Configuration

### Environment Variables

- `DRY_RUN`: Set to `true` to run in dry-run mode (development only)
- `VAULT_PATH`: Path to the AI Employee vault (default: ./AI_Employee_Vault)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Folder Structure

- `Inbox/`: Incoming tasks to be processed
- `Needs_Action/`: Tasks waiting for Claude Code processing
- `Done/`: Completed tasks
- `Logs/`: System logs and activity records
- `Pending_Approval/`: Tasks awaiting human approval
- `Approved/`: Approved tasks ready for execution

## Security

- All data remains on your local machine
- Credentials stored only in `.env` file (not committed to git)
- Human-in-the-loop approval required for external actions
- Comprehensive logging for audit trail

## Development

### Running in Development Mode

```bash
# Set DRY_RUN=true in .env to prevent actual external actions
DRY_RUN=true python -m src.filesystem_watcher
```

### Project Structure

```
personal-ai-employee/
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
├── src/
│   ├── base_watcher.py
│   └── filesystem_watcher.py
├── AI_Employee_Vault/
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── skills/
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Done/
│   ├── Logs/
│   ├── Pending_Approval/
│   └── Approved/
└── scripts/
    └── run_claude.sh
```

## Troubleshooting

- Check the log files in `AI_Employee_Vault/Logs/` for error messages
- Ensure Claude Code is properly configured and authenticated
- Verify that the vault folder structure exists and has proper permissions

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for discussion.

## License

MIT
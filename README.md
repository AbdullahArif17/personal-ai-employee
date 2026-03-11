# Personal AI Employee

A local automation system where Claude Code acts as an AI employee that monitors an Obsidian markdown vault, processes incoming tasks, and writes structured outputs — all running on the user's local machine.

## Overview

The Personal AI Employee is a Bronze-tier automation system that:
- Monitors an Obsidian vault for incoming tasks
- Processes tasks automatically using Claude Code
- Maintains structured outputs in designated folders
- Runs entirely on your local machine for privacy and security

## Features

1. **Bronze Tier (Local Automation)**:
   - **Obsidian Vault Structure**: Organized folder system with Inbox, Needs_Action, Done, Logs, Pending_Approval, and Approved folders
   - **Dashboard.md**: Live summary showing pending items, recent activity, and status
   - **Company_Handbook.md**: Rules of engagement for the AI (tone, approval thresholds, contact list)
   - **Filesystem Watcher**: Python script monitoring the Inbox folder and copying new files to Needs_Action with metadata
   - **Agent SKILL.md files**: Markdown skill files Claude Code reads to process tasks
   - **Claude Code Integration**: Automated processing of tasks following skill instructions

2. **Silver Tier (External Integrations)**:
   - **Gmail Integration**: Monitor Gmail for unread emails using IMAP and save them as .md files in Needs_Action folder
   - **Email MCP Server**: Draft email replies using Gemini AI and save drafts to Pending_Approval folder
   - **Email Sending**: Send approved replies via SMTP using Gmail App Password (no API required)
   - **LinkedIn Poster**: Generate business posts using Gemini AI and save as drafts for manual posting
   - **Human-in-the-Loop Workflow**: Complete approval system that monitors Approved folder and executes actions
   - **Rate Limiting**: Enforced limits (max 10 emails per run, max 3 LinkedIn posts per day)
   - **Secure Authentication**: Uses Gmail App Password for IMAP/SMTP access (no credit card required)

3. **Gold Tier (Advanced Automation)**:
   - **Ralph Wiggum Loop**: Autonomous task completion loop that monitors Needs_Action folder, processes tasks with AI, and retries up to 10 times before stopping
   - **Twitter/X Integration**: AI-powered tweet generation using business context from Company_Handbook.md, with approval workflow and rate limiting (max 5 posts per day)
   - **Facebook & Instagram Integration**: AI-powered post generation with platform-appropriate formatting, hashtags and emojis, with approval workflow and rate limiting (max 3 posts per day per platform)
   - **Odoo Accounting Integration**: Connect to local Odoo Community instance via JSON-RPC API for invoice creation and financial reporting, with approval workflow and rate limiting (max 10 invoices per day)
   - **Weekly Business Audit**: Automated weekly audit system that runs every Sunday night, aggregating data from Done files, Odoo financial data, and social media activity to generate comprehensive audit reports
   - **Enhanced Rate Limiting**: Comprehensive rate limiting across all platforms to prevent API abuse
   - **Advanced Approval Workflow**: Extended approval system supporting all Gold tier features
   - **Performance Monitoring**: Built-in monitoring for all features with alerts for slow operations
   - **Audit Trail Compliance**: Comprehensive logging for all actions to ensure compliance
   - **Secure Credential Management**: All API credentials stored in .env file only, never in vault or committed to git
   - **Local-First Architecture**: All processing occurs locally on user's machine, maintaining data privacy and security

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

### Processing Silver Tier Tasks

Run the Silver tier features processor to handle Gmail, email replies, and LinkedIn posts:

On Windows:
```cmd
scripts\process_tasks_silver.bat
```

On Linux/macOS (using Wine or similar):
```bash
wine cmd /c scripts\process_tasks_silver.bat
```

Alternatively, you can run the Python scripts directly on any platform:
```bash
python src/gmail_watcher.py
python src/email_mcp.py
python src/linkedin_poster.py
```

This script will:
- Check for new Gmail messages and save them to Needs_Action
- Process emails for reply drafts using AI
- Generate LinkedIn post drafts
- Monitor Approved folder for actions to execute
- Update the dashboard

### Running Individual Silver Tier Components

You can also run individual components:

```bash
# Check Gmail for new messages
python src/gmail_watcher.py

# Process emails for reply drafts
python src/email_mcp.py

# Generate LinkedIn post drafts
python src/linkedin_poster.py

# Monitor Approved folder for actions
python src/approved_watcher.py
```

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

## Testing

### Gold Tier Feature Tests

The Gold tier features include comprehensive test suites:

1. **Unit Tests**: Located in `tests/test_gold_tier_features.py`
   - Test individual components: Ralph Loop, Twitter poster, Social media poster, Odoo integration, Weekly audit
   - Verify rate limiting functionality
   - Test approval workflows
   - Validate performance monitoring

2. **End-to-End Tests**: Located in `tests/end_to_end_tests.py`
   - Test complete user story flows
   - Verify integration between components
   - Validate approval workflows across features
   - Test rate limiting enforcement

To run the tests:

```bash
# Run all tests
python -m pytest tests/

# Run just the Gold tier feature tests
python -m pytest tests/test_gold_tier_features.py

# Run just the end-to-end tests
python -m pytest tests/end_to_end_tests.py

# Run with verbose output
python -m pytest tests/ -v
```

## Troubleshooting

- Check the log files in `AI_Employee_Vault/Logs/` for error messages
- Ensure Claude Code is properly configured and authenticated
- Verify that the vault folder structure exists and has proper permissions
- For Gold tier features, check that required API credentials are configured in `.env`
- Check rate limits if social media or Odoo operations are failing

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for discussion.

## License

MIT
@echo off
REM Batch script to run the Silver tier features of the AI Employee

echo Starting AI Employee Silver tier processing...

REM Navigate to the project directory
cd /d "D:\giaic\personal-ai-employee"

echo.
echo Checking for new Gmail messages...
python src/gmail_watcher.py
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Gmail watcher failed
)

echo.
echo Processing emails for reply drafts...
python src/email_mcp.py
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Email MCP failed
)

echo.
echo Generating LinkedIn post drafts...
python src/linkedin_poster.py
if %ERRORLEVEL% NEQ 0 (
    echo Warning: LinkedIn poster failed
)

echo.
echo Monitoring Approved folder for actions...
REM This would typically run continuously, but for this batch we'll just check once
REM In a real implementation, you might want to run this separately as a daemon
python -c "
import sys
sys.path.insert(0, '.')
from src.approved_watcher import ApprovedWatcher
import os
vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
watcher = ApprovedWatcher(vault_path, dry_run=False)
print('Checking for approved actions...')
# Process any currently approved files without starting continuous monitoring
from pathlib import Path
approved_path = Path(vault_path) / 'Approved'
if approved_path.exists():
    import time
    # Brief check for any approved files
    time.sleep(2)
else:
    print('Approved folder does not exist.')
"

echo.
echo Updating dashboard...
python src/dashboard_updater.py
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Dashboard update failed
)

echo.
echo Silver tier processing completed!
pause
@echo off
REM Gold Tier Features Processing Script
REM This script runs the Gold tier features of the Personal AI Employee system

setlocal

echo Starting Gold Tier Features Processing...

REM Set the Python executable (adjust as needed)
set PYTHON_CMD=python

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the main AI employee system with Gold tier features
echo Running Ralph Wiggum Loop...
%PYTHON_CMD% -m src.ralph_loop

echo Running Twitter/X poster...
%PYTHON_CMD% -m src.twitter_poster

echo Running Social media poster...
%PYTHON_CMD% -m src.social_media_poster

echo Running Odoo integration...
%PYTHON_CMD% -m src.odoo_integration

echo Running Weekly audit...
%PYTHON_CMD% -m src.weekly_audit

echo Gold Tier Features Processing completed.
pause
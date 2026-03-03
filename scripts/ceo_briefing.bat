@echo off
REM CEO Briefing Generator for Personal AI Employee
REM Generates a weekly executive summary of AI employee activities

echo.
echo ========================================
echo   CEO BRIEFING GENERATOR
echo ========================================
echo.

REM Navigate to the project directory
cd /d "D:\giaic\personal-ai-employee"

echo Running CEO Briefing Generator...
echo.

REM Run the CEO briefing script
python src\ceo_briefing.py

echo.
echo ========================================
echo   CEO BRIEFING COMPLETE
echo ========================================
echo.

pause
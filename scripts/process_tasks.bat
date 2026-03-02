@echo off
REM Batch script to run the AI processor for the Personal AI Employee

echo Starting AI Employee task processing...

REM Navigate to the project directory
cd /d "D:\giaic\personal-ai-employee"

REM Run the AI processor
python src/ai_processor.py

echo.
echo Task processing completed!
pause
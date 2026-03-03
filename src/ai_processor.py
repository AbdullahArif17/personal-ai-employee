"""
AI Processor for the Personal AI Employee system.
Processes files using the Google Gemini API.
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from google import genai
except ImportError:
    print("Error: google-genai library is not installed.")
    print("Please install it using: pip install google-genai")
    exit(1)

class AIProcessor:
    """Processes files using the Gemini API."""

    def __init__(self):
        # Use absolute paths as specified
        self.vault_path = Path("D:/giaic/personal-ai-employee/AI_Employee_Vault")
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.logs_path = self.vault_path / "Logs"

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file")

        self.client = genai.Client(api_key=api_key)

        # Create directories if they don't exist
        self.needs_action_path.mkdir(exist_ok=True)
        self.done_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)

    def process_files(self):
        """Process all eligible files in the Needs_Action folder."""
        print(f"Starting AI processing for vault: {self.vault_path}")

        # Find all .txt and .md files in Needs_Action directory
        files = list(self.needs_action_path.glob("*.txt")) + list(self.needs_action_path.glob("*.md"))
        files = [f for f in files if f.is_file()]

        if not files:
            print(f"No .txt or .md files to process in {self.needs_action_path}")
            return

        print(f"Found {len(files)} file(s) to process")

        for file_path in files:
            self.process_single_file(file_path)

        # Update dashboard after processing
        self.update_dashboard()
        print("AI processing completed.")

    def process_single_file(self, file_path: Path):
        """Process a single file using the Gemini API."""
        print(f"Processing file: {file_path.name}")

        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Read the triage skill to understand how to process the content
            skill_file = self.vault_path / "skills" / "SKILL_triage.md"
            skill_content = ""
            if skill_file.exists():
                with open(skill_file, 'r', encoding='utf-8') as f:
                    skill_content = f.read()

            # Create the prompt for Gemini
            prompt = f"""
{skill_content}

The current task is:
{content}

Please process this task according to the guidelines above. Provide a clear, actionable response.
"""

            # Call the Gemini API
            response = self.client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt
            )

            # Get the processed content
            processed_content = response.text if response.text else "No response generated"

            # Create the output filename with .md extension for Obsidian
            output_filename = f"DONE_{file_path.stem}.md"
            output_file_path = self.done_path / output_filename

            # Write the processed content to the output file
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# Response to: {file_path.name}\n\n")
                f.write(processed_content)
                f.write(f"\n\n*Processed by AI Employee on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

            # Log the processing action
            self.log_action("FILE_PROCESSED", f"Processed {file_path.name} with Gemini API")

            # Optionally, move the original file to prevent reprocessing
            # (keeping it for now as it might be needed for reference)

            print(f"File {file_path.name} processed successfully")

        except Exception as e:
            error_msg = f"Error processing file {file_path.name}: {str(e)}"
            print(error_msg)
            self.log_action("ERROR", error_msg)

    def log_action(self, action_type: str, message: str):
        """Log an action to the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "action": action_type,
            "message": message,
            "processor": "Gemini"
        }

        # Create log filename based on today's date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"{today}.json"

        # Read existing log entries or initialize empty list
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write updated logs back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)

    def update_dashboard(self):
        """Update the dashboard with recent activity."""
        dashboard_path = self.vault_path / "Dashboard.md"

        # Count pending tasks in Needs_Action
        pending_files = list(self.needs_action_path.glob("*.txt")) + list(self.needs_action_path.glob("*.md"))
        pending_count = len([f for f in pending_files if f.is_file()])

        # Get recent activity from today's log
        today = datetime.now().strftime("%Y-%m-%d")
        today_log = self.logs_path / f"{today}.json"
        recent_activity = []

        if today_log.exists():
            try:
                with open(today_log, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    # Get last 5 activities
                    recent_logs = logs[-5:] if isinstance(logs, list) else []
                    for log in recent_logs:
                        recent_activity.append(f"- {log['timestamp']}: {log['message']}")
            except json.JSONDecodeError:
                recent_activity = ["- Could not read today's logs"]

        # Create dashboard content
        dashboard_content = f"""# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Pending Tasks
- **{pending_count}** tasks awaiting processing

## Recent Activity
"""

        if recent_activity:
            dashboard_content += "\n".join(recent_activity)
        else:
            dashboard_content += "- No recent activity"

        dashboard_content += """

## System Status
- AI Processor: **Ready**
- Last Run: **""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """**
- Processing Engine: **Gemini API**

## Directories
- Needs Action: """ + str(self.needs_action_path) + """
- Done: """ + str(self.done_path) + """
- Logs: """ + str(self.logs_path) + """
"""

        # Write the dashboard
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_content)


def main():
    """Main function to run the AI processor."""
    processor = AIProcessor()
    processor.process_files()


if __name__ == "__main__":
    main()
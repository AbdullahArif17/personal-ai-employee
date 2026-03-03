"""
Gemini processor for the Personal AI Employee system.
Processes files in the Needs_Action folder using the Gemini API.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from google import genai
from dotenv import load_dotenv

from dashboard_updater import DashboardUpdater

# Load environment variables
load_dotenv()

class GeminiProcessor:
    """Processes files using the Gemini API."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.logs_path = self.vault_path / "Logs"

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        self.client = genai.Client(api_key=api_key)

        # Set up dashboard updater
        self.dashboard_updater = DashboardUpdater(vault_path)

    def process_files(self):
        """Process all files in the Needs_Action folder."""
        print(f"Starting Gemini processing for vault: {self.vault_path}")

        # Find all files in Needs_Action directory
        files = list(self.needs_action_path.glob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]

        if not files:
            print(f"No files to process in {self.needs_action_path}")
            return

        print(f"Found {len(files)} file(s) to process")

        for file_path in files:
            self.process_single_file(file_path)

        # Update dashboard after processing
        self.dashboard_updater.update_dashboard()
        print("Gemini processing completed.")

    def process_single_file(self, file_path: Path):
        """Process a single file using the Gemini API."""
        print(f"Processing file: {file_path.name}")

        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine if the file requires approval by looking for approval indicators
            requires_approval = self._check_approval_needed(content)

            # Prepare the prompt for Gemini
            prompt = self._create_prompt(content, file_path.name)

            # Call the Gemini API
            response = self.client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt
            )

            # Get the processed content
            processed_content = response.text if response.text else "No response generated"

            # Determine target directory based on approval requirement
            if requires_approval:
                target_dir = self.pending_approval_path
                status_msg = "moved to Pending Approval"
            else:
                target_dir = self.done_path
                status_msg = "moved to Done"

            # Create target directory if it doesn't exist
            target_dir.mkdir(exist_ok=True)

            # Create target file path (handle potential name conflicts)
            target_file_path = self._get_unique_filename(target_dir, file_path.name)

            # Write the processed content to the target file
            with open(target_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)

            # Process any associated metadata file
            metadata_file = self.needs_action_path / f"{file_path.stem}_metadata.json"
            if metadata_file.exists():
                target_metadata_path = target_dir / f"{target_file_path.stem}_metadata.json"
                shutil.move(str(metadata_file), str(target_metadata_path))

            # Move the original file to avoid re-processing
            original_backup_path = target_dir / f"original_{file_path.name}"
            shutil.move(str(file_path), str(original_backup_path))

            print(f"File {file_path.name} processed and {status_msg}")

            # Log the action
            self._log_action("FILE_PROCESSED", f"Processed {file_path.name} with Gemini, {status_msg}")

        except Exception as e:
            error_msg = f"Error processing file {file_path.name}: {str(e)}"
            print(error_msg)
            self._log_action("ERROR", error_msg)

    def _check_approval_needed(self, content: str) -> bool:
        """Check if the content requires approval."""
        content_lower = content.lower()
        approval_indicators = [
            '$approval_required', 'requires approval', 'needs approval',
            'need approval', 'approve', 'authorization needed', 'permission required',
            'expensive', 'cost', 'payment', 'buy', 'purchase', 'money', 'budget'
        ]

        return any(indicator in content_lower for indicator in approval_indicators)

    def _create_prompt(self, content: str, filename: str) -> str:
        """Create a prompt for the Gemini API based on the file content and skills."""
        # Read the skill files to understand how to process the content
        skills_dir = self.vault_path / "skills"
        skills_text = ""

        if skills_dir.exists():
            for skill_file in skills_dir.glob("*.md"):
                try:
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        skills_text += f"\n--- SKILL: {skill_file.name} ---\n{f.read()}\n"
                except Exception as e:
                    print(f"Could not read skill file {skill_file}: {e}")

        # Create the full prompt
        prompt = f"""
You are an AI Employee processing a task. Here are the skills you should follow:

{skills_text}

The current task is in file: {filename}

The content of the task is:
{content}

Please process this task according to the skills provided above. Provide a complete response that addresses the task requirements. Format your response appropriately based on the task type.
"""
        return prompt

    def _get_unique_filename(self, directory: Path, filename: str) -> Path:
        """Get a unique filename by appending a number if the file already exists."""
        target_path = directory / filename
        if not target_path.exists():
            return target_path

        stem = Path(filename).stem
        suffix = Path(filename).suffix
        counter = 1

        while target_path.exists():
            new_filename = f"{stem}_{counter}{suffix}"
            target_path = directory / new_filename
            counter += 1

        return target_path

    def _log_action(self, action_type: str, message: str):
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

        # Create logs directory if it doesn't exist
        self.logs_path.mkdir(exist_ok=True)

        # Write updated logs back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)


def main():
    """Main function to run the Gemini processor."""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    processor = GeminiProcessor(vault_path)
    processor.process_files()


if __name__ == "__main__":
    main()
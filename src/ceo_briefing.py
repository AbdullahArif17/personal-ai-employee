"""
CEO Briefing Generator for the Personal AI Employee system.
Generates a weekly executive summary of AI employee activities.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()


class CEOBriefing:
    """CEO briefing generator implementation for the Personal AI Employee."""

    def __init__(self, vault_path: str = "D:/giaic/personal-ai-employee/AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.done_path = self.vault_path / "Done"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.dashboard_path = self.vault_path / "Dashboard.md"

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set in .env file")

        self.client = genai.Client(api_key=api_key)

    def count_recent_done_files(self) -> int:
        """
        Count all files in Done/ folder from last 7 days.

        Returns:
            Number of files created in the last 7 days
        """
        seven_days_ago = datetime.now() - timedelta(days=7)
        count = 0

        for file_path in self.done_path.glob("*.md"):
            if file_path.is_file():
                # Check if file was modified in the last 7 days
                if datetime.fromtimestamp(file_path.stat().st_mtime) >= seven_days_ago:
                    count += 1

        return count

    def count_needs_action_files(self) -> int:
        """
        Count all files in Needs_Action/ folder (pending).

        Returns:
            Number of pending files
        """
        count = 0
        for file_path in self.needs_action_path.glob("*.md"):
            if file_path.is_file():
                count += 1
        return count

    def read_dashboard(self) -> str:
        """
        Read Dashboard.md current status.

        Returns:
            Dashboard content as string
        """
        try:
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Dashboard not found"
        except Exception as e:
            print(f"Error reading dashboard: {e}")
            return "Error reading dashboard"

    def read_recent_done_files(self) -> str:
        """
        Read all .md files in Done/ from last 7 days.

        Returns:
            Combined content of recent files
        """
        seven_days_ago = datetime.now() - timedelta(days=7)
        content = []

        for file_path in self.done_path.glob("*.md"):
            if file_path.is_file():
                # Check if file was modified in the last 7 days
                if datetime.fromtimestamp(file_path.stat().st_mtime) >= seven_days_ago:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content.append(f"---\nFile: {file_path.name}\n---\n{f.read()}\n")
                    except Exception as e:
                        print(f"Error reading file {file_path.name}: {e}")

        return "\n".join(content)

    def generate_ceo_briefing(self) -> str:
        """
        Generate CEO briefing with Gemini including specified sections.

        Returns:
            Generated CEO briefing content
        """
        # Collect data
        tasks_completed = self.count_recent_done_files()
        tasks_pending = self.count_needs_action_files()
        dashboard_content = self.read_dashboard()
        recent_done_content = self.read_recent_done_files()

        prompt = f"""
Generate a CEO briefing based on the following data from the Personal AI Employee system:

Dashboard Status:
{dashboard_content}

Recent Completed Tasks (last 7 days):
{recent_done_content}

Statistics:
- Tasks completed in last 7 days: {tasks_completed}
- Tasks pending in Needs_Action: {tasks_pending}

Please generate a comprehensive CEO briefing with these sections:

## Executive Summary
Provide a high-level overview of the week's accomplishments and status.

## This Week Stats
- Tasks completed: {tasks_completed}
- Emails processed: [Estimate based on file names]
- Posts generated: [Estimate based on file names]

## Highlights
Key accomplishments and successful completions from the week.

## Bottlenecks
Any issues, delays, or challenges encountered.

## Proactive Suggestions
Recommendations for improvements or optimizations.

## Next Week Priorities
Top priorities and recommendations for the upcoming week.

Format the response in Markdown with clear sections and professional language suitable for a CEO.
"""

        try:
            response = self.client.models.generate_content(
                model="gemma-3-27b-it",
                contents=prompt
            )
            return response.text if response.text else "No content generated"
        except Exception as e:
            print(f"❌ Error generating CEO briefing with Gemini: {e}")
            return f"""# CEO Briefing - {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
Failed to generate briefing due to an error with the AI service.

## This Week Stats
- Tasks completed: {tasks_completed}
- Tasks pending: {tasks_pending}
- Emails processed: Unknown
- Posts generated: Unknown

## Highlights
None available due to AI generation error.

## Bottlenecks
AI service unavailable for analysis.

## Proactive Suggestions
Check API configuration and connectivity.

## Next Week Priorities
Retry AI service and ensure proper configuration.
"""

    def save_briefing_report(self, content: str) -> str:
        """
        Save the CEO briefing report.

        Args:
            content: CEO briefing content to save

        Returns:
            Filename of the saved report
        """
        # Create filename with current date
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"CEO_Briefing_{date_str}.md"
        filepath = self.vault_path / filename

        # Write the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"📄 Saved CEO briefing: {filepath.name}")

        return filepath.name

    def update_dashboard(self, tasks_completed: int):
        """
        Update Dashboard.md to show last briefing date and weekly stats.

        Args:
            tasks_completed: Number of tasks completed this week
        """
        try:
            # Read current dashboard content
            if self.dashboard_path.exists():
                with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"""# AI Employee Dashboard

**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Update the dashboard with briefing information
            # Find and update the status section or add it if not found
            if "**Last Briefing**:" in content:
                # Update existing briefing info
                lines = content.split('\n')
                updated_lines = []
                for line in lines:
                    if line.startswith('- **Last Briefing**:'):
                        updated_lines.append(f"- **Last Briefing**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    elif line.startswith('- **Weekly Stats**:'):
                        updated_lines.append(f"- **Weekly Stats**: {tasks_completed} tasks completed")
                    else:
                        updated_lines.append(line)
                content = '\n'.join(updated_lines)
            else:
                # Add briefing info to the system status section
                if '## System Status' in content:
                    # Insert briefing info after the system status heading
                    parts = content.split('## System Status')
                    if len(parts) > 1:
                        content = f"{parts[0]}## System Status\n- **Last Briefing**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- **Weekly Stats**: {tasks_completed} tasks completed\n{parts[1]}"
                else:
                    # Add system status section with briefing info
                    content += f"""

## System Status
- **Last Briefing**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Weekly Stats**: {tasks_completed} tasks completed
"""

            # Write updated content back to dashboard
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print("✅ Dashboard updated with briefing information")

        except Exception as e:
            print(f"❌ Error updating dashboard: {e}")

    def generate_and_save_briefing(self) -> str:
        """
        Generate the CEO briefing and save it.

        Returns:
            Filename of the saved briefing
        """
        print("🔄 Generating CEO Briefing...")

        # Collect initial stats
        tasks_completed = self.count_recent_done_files()

        # Generate the briefing content
        content = self.generate_ceo_briefing()

        # Print the generated briefing to console
        print("\n" + "="*70)
        print("CEO BRIEFING REPORT")
        print("="*70)
        print(content)
        print("="*70 + "\n")

        # Save the briefing report
        filename = self.save_briefing_report(content)

        # Update the dashboard with briefing information
        self.update_dashboard(tasks_completed)

        print(f"✅ CEO briefing saved to: {self.vault_path / filename}")

        return filename


def main():
    """Main function to run the CEO briefing generator."""
    print("🚀 Starting CEO Briefing Generator")
    print("📋 This will generate a weekly executive summary")
    print("-" * 60)

    vault_path = os.getenv('VAULT_PATH', 'D:/giaic/personal-ai-employee/AI_Employee_Vault')

    briefing = CEOBriefing(vault_path)

    # Generate and save the CEO briefing
    filename = briefing.generate_and_save_briefing()
    print(f"🎯 CEO briefing generation completed: {filename}")


if __name__ == "__main__":
    main()
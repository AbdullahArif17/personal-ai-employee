"""
Dashboard updater for the Personal AI Employee system.
Updates the Dashboard.md file with current status information.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DashboardUpdater:
    """Manages updating the Dashboard.md file with current status information."""

    def __init__(self, vault_path: str = "./AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / "Dashboard.md"

    def update_dashboard(self) -> bool:
        """
        Update the dashboard with current status information.

        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Read the current dashboard content
            if self.dashboard_path.exists():
                with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()
            else:
                # If dashboard doesn't exist, create a basic one
                current_content = self._get_default_dashboard_content()

            # Parse the current content to preserve non-status sections
            header_section, status_table, recent_activity, system_status, stats_section, footer_section = \
                self._parse_dashboard_sections(current_content)

            # Generate updated content
            updated_content = self._generate_updated_content(
                header_section,
                status_table,
                recent_activity,
                system_status,
                stats_section,
                footer_section
            )

            # Write the updated dashboard
            with open(self.dashboard_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            return True

        except Exception as e:
            print(f"Error updating dashboard: {e}")
            return False

    def _get_default_dashboard_content(self) -> str:
        """Generate default dashboard content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# AI Employee Dashboard

**Last Updated**: {timestamp}

## Status Overview

| Folder | Count | Description |
|--------|-------|-------------|
| Inbox | 0 | New tasks waiting to be processed |
| Needs Action | 0 | Tasks ready for Claude Code processing |
| Done | 0 | Completed tasks |
| Pending Approval | 0 | Tasks awaiting human approval |
| Approved | 0 | Approved tasks ready for execution |
| Logs | 0 | System logs and activity records |

## Recent Activity

*No recent activity*

## System Status

- Filesystem watcher: **Inactive**
- Claude Code integration: **Not configured**
- Last run: **Never**
- DRY_RUN mode: **Enabled**

## Quick Links

- [Company Handbook](./Company_Handbook.md)
- [Skills Directory](./skills/)
- [Inbox](./Inbox/)
- [Needs Action](./Needs_Action/)
- [Done](./Done/)
- [Pending Approval](./Pending_Approval/)
- [Approved](./Approved/)
- [Logs](./Logs/)

## Statistics

- Total processed: 0
- Today's activity: 0
- Success rate: 0%
- Error count: 0
"""

    def _parse_dashboard_sections(self, content: str) -> tuple:
        """Parse dashboard content into sections."""
        # Default values
        header_section = "# AI Employee Dashboard\n\n"
        status_table = ""
        recent_activity = "## Recent Activity\n\n*No recent activity*\n"
        system_status = "## System Status\n\n- Filesystem watcher: **Inactive**\n- Claude Code integration: **Not configured**\n- Last run: **Never**\n- DRY_RUN mode: **Enabled**\n"
        stats_section = "## Statistics\n\n- Total processed: 0\n- Today's activity: 0\n- Success rate: 0%\n- Error count: 0\n"
        footer_section = ""

        lines = content.split('\n')
        current_section = "header"

        for i, line in enumerate(lines):
            if line.startswith("## Status Overview"):
                current_section = "status_table"
                header_section = "\n".join(lines[:i]) + "\n"
            elif line.startswith("## Recent Activity"):
                current_section = "recent_activity"
                status_table = "\n".join(lines[len(header_section.split('\n')):i]) + "\n"
            elif line.startswith("## System Status"):
                current_section = "system_status"
                recent_activity = "\n".join(lines[len((header_section + status_table).split('\n')):i]) + "\n"
            elif line.startswith("## Statistics"):
                current_section = "stats"
                system_status = "\n".join(lines[len((header_section + status_table + recent_activity).split('\n')):i]) + "\n"
            elif line.startswith("## Quick Links"):
                current_section = "footer"
                stats_section = "\n".join(lines[len((header_section + status_table + recent_activity + system_status).split('\n')):i]) + "\n"
                footer_section = "\n".join(lines[i:])
                break

        # If we didn't find all sections, use what we parsed
        if current_section != "footer":
            if current_section == "status_table":
                status_table = "\n".join(lines[len(header_section.split('\n')):]) + "\n"
            elif current_section == "recent_activity":
                recent_activity = "\n".join(lines[len((header_section + status_table).split('\n')):]) + "\n"
            elif current_section == "system_status":
                system_status = "\n".join(lines[len((header_section + status_table + recent_activity).split('\n')):]) + "\n"
            elif current_section == "stats":
                stats_section = "\n".join(lines[len((header_section + status_table + recent_activity + system_status).split('\n')):]) + "\n"

        return header_section, status_table, recent_activity, system_status, stats_section, footer_section

    def _generate_updated_content(
        self,
        header_section: str,
        status_table: str,
        recent_activity: str,
        system_status: str,
        stats_section: str,
        footer_section: str
    ) -> str:
        """Generate the updated dashboard content with fresh data."""
        # Update the timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_section = header_section.replace(
            "Last Updated**: [timestamp]",
            f"Last Updated**: {timestamp}"
        )
        if "Last Updated**:" not in header_section:
            header_section = header_section.replace(
                "# AI Employee Dashboard",
                f"# AI Employee Dashboard\n\n**Last Updated**: {timestamp}"
            )

        # Get updated counts
        folder_counts = self._get_folder_counts()

        # Update status table
        status_table = self._update_status_table(folder_counts)

        # Update system status if possible
        # For now, we'll keep the existing system status as it may have been manually updated
        # In a real implementation, we might want to dynamically update this

        # Update statistics
        stats_section = self._update_statistics(folder_counts)

        # Combine all sections
        return f"{header_section}{status_table}{recent_activity}{system_status}{stats_section}{footer_section}"

    def _get_folder_counts(self) -> Dict[str, int]:
        """Count files in each vault folder."""
        counts = {}
        folders = {
            "Inbox": "Inbox",
            "Needs Action": "Needs_Action",
            "Done": "Done",
            "Pending Approval": "Pending_Approval",
            "Approved": "Approved",
            "Logs": "Logs"
        }

        for display_name, folder_name in folders.items():
            folder_path = self.vault_path / folder_name
            if folder_path.exists():
                try:
                    # Count files (not subdirectories)
                    count = sum(1 for item in folder_path.iterdir() if item.is_file())
                    counts[display_name] = count
                except Exception:
                    counts[display_name] = 0  # Error occurred, show 0
            else:
                counts[display_name] = 0  # Folder doesn't exist, show 0

        return counts

    def _update_status_table(self, folder_counts: Dict[str, int]) -> str:
        """Update the status overview table with current counts."""
        table_content = "## Status Overview\n\n"
        table_content += "| Folder | Count | Description |\n"
        table_content += "|--------|-------|-------------|\n"

        descriptions = {
            "Inbox": "New tasks waiting to be processed",
            "Needs Action": "Tasks ready for Claude Code processing",
            "Done": "Completed tasks",
            "Pending Approval": "Tasks awaiting human approval",
            "Approved": "Approved tasks ready for execution",
            "Logs": "System logs and activity records"
        }

        for folder_name, count in folder_counts.items():
            description = descriptions.get(folder_name, "Folder contents")
            table_content += f"| {folder_name} | {count} | {description} |\n"

        return table_content + "\n"

    def _update_statistics(self, folder_counts: Dict[str, int]) -> str:
        """Update the statistics section."""
        total_processed = folder_counts.get("Done", 0)
        pending_count = folder_counts.get("Inbox", 0) + folder_counts.get("Needs Action", 0)
        error_logs = folder_counts.get("Logs", 0)  # This is a simplification

        # Calculate success rate - for now, we'll calculate based on done vs pending
        total_tasks = total_processed + pending_count
        success_rate = (total_processed / total_tasks * 100) if total_tasks > 0 else 0

        # Get today's date for "today's activity"
        today_str = datetime.now().strftime("%Y-%m-%d")

        # For today's activity, we'll look for log files from today
        today_logs_path = self.vault_path / "Logs" / f"{today_str}.json"
        today_activity = 0
        if today_logs_path.exists():
            try:
                with open(today_logs_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    today_activity = len(logs) if isinstance(logs, list) else 0
            except:
                today_activity = 0  # If there's an error reading logs, show 0

        stats_content = "## Statistics\n\n"
        stats_content += f"- Total processed: {total_processed}\n"
        stats_content += f"- Today's activity: {today_activity}\n"
        stats_content += f"- Success rate: {success_rate:.1f}%\n"
        stats_content += f"- Error count: {error_logs}\n\n"

        return stats_content

    def update_system_status(self, watcher_status: str = "Inactive",
                           claude_status: str = "Not configured",
                           last_run: str = "Never",
                           dry_run: bool = True):
        """Update the system status section."""
        status_text = "## System Status\n\n"
        status_text += f"- Filesystem watcher: **{watcher_status}**\n"
        status_text += f"- Claude Code integration: **{claude_status}**\n"
        status_text += f"- Last run: **{last_run}**\n"
        status_text += f"- DRY_RUN mode: **{'Enabled' if dry_run else 'Disabled'}**\n\n"

        # We'll update this in the main dashboard when update_dashboard() is called
        pass


def main():
    """Main function to update the dashboard."""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    updater = DashboardUpdater(vault_path)
    success = updater.update_dashboard()

    if success:
        print("Dashboard updated successfully!")
    else:
        print("Failed to update dashboard.")


if __name__ == "__main__":
    main()
'''
Weekly audit for the Personal AI Employee system.
Runs automatically every Sunday night and generates comprehensive business reports.
'''

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import schedule separately to handle if it's not available
try:
    import schedule
except ImportError:
    print("Warning: schedule library not installed. Please install it with: pip install schedule")
    schedule = None

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger, AuditLogger
    from .config import get_config
    from .file_utils import get_file_utils
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger, AuditLogger
    from config import get_config
    from file_utils import get_file_utils

logger = setup_logger('weekly_audit')
audit_logger = AuditLogger('weekly_audit')
config = get_config()
file_utils = get_file_utils()

# Lazy import for OdooIntegration to avoid circular imports
def get_odoo_integration():
    try:
        from .financial_odoo_integration import OdooIntegration
    except ImportError:
        from financial_odoo_integration import OdooIntegration
    return OdooIntegration()


class WeeklyAudit:
    """
    Weekly audit implementation for the Personal AI Employee system.
    Runs automatically every Sunday night and generates comprehensive business reports.
    """

    def __init__(self):
        """Initialize the weekly audit."""
        pass

    def get_done_files_last_week(self) -> List[Path]:
        """
        Get all files from the Done folder from the past 7 days.

        Returns:
            List of file paths from the Done folder in the last 7 days
        """
        done_path = Path(config.vault_path) / "Done"
        if not done_path.exists():
            logger.warning(f"Done folder does not exist: {done_path}")
            return []

        files = []
        seven_days_ago = datetime.now() - timedelta(days=7)

        for file_path in done_path.iterdir():
            if file_path.is_file():
                # Get file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mod_time >= seven_days_ago:
                    files.append(file_path)

        logger.info(f"Found {len(files)} files in Done folder from the last 7 days")
        return files

    def get_odoo_financial_data_last_week(self) -> Dict[str, Any]:
        """
        Get financial data from Odoo from the past week.

        Returns:
            Dictionary containing financial data from Odoo
        """
        try:
            # Get Odoo integration instance
            odoo_integration = get_odoo_integration()

            # Test connection first
            success, message = odoo_integration.test_connection()
            if not success:
                logger.warning(f"Odoo connection failed: {message}")
                # Return empty financial data with error info
                return {
                    'period': {'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                              'to': datetime.now().strftime('%Y-%m-%d')},
                    'transactions': [],
                    'metrics': {
                        'total_revenue': 0,
                        'total_expenses': 0,
                        'outstanding_payments': 0,
                        'transaction_count': 0,
                        'average_transaction_value': 0
                    },
                    'error': message
                }

            # Get financial summary
            financial_summary = odoo_integration.get_financial_summary()

            # Get transactions
            transactions = odoo_integration.get_transactions(limit=20)

            # Calculate additional metrics
            transaction_count = len(transactions) if isinstance(transactions, list) else 0
            total_revenue = financial_summary.get('total_invoiced', 0) if isinstance(financial_summary, dict) else 0
            total_expenses = financial_summary.get('total_expenses', 0) if isinstance(financial_summary, dict) else 0
            average_transaction_value = total_revenue / transaction_count if transaction_count > 0 else 0

            financial_data = {
                'period': financial_summary.get('period', 'Last 30 days') if isinstance(financial_summary, dict) else 'Last 30 days',
                'transactions': transactions if isinstance(transactions, list) else [],
                'metrics': {
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'outstanding_payments': financial_summary.get('outstanding_payments', 0) if isinstance(financial_summary, dict) else 0,
                    'transaction_count': transaction_count,
                    'average_transaction_value': average_transaction_value
                }
            }

            logger.info(f"Retrieved financial data from Odoo: {transaction_count} transactions, "
                       f"Revenue: ${total_revenue:.2f}, Expenses: ${total_expenses:.2f}")
            return financial_data

        except Exception as e:
            logger.error(f"Error retrieving Odoo financial data: {e}")
            # Return empty financial data with error info
            return {
                'period': {'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                          'to': datetime.now().strftime('%Y-%m-%d')},
                'transactions': [],
                'metrics': {
                    'total_revenue': 0,
                    'total_expenses': 0,
                    'outstanding_payments': 0,
                    'transaction_count': 0,
                    'average_transaction_value': 0
                },
                'error': str(e)
            }

    def get_social_media_activity_last_week(self) -> Dict[str, Any]:
        """
        Get social media activity from the past week.

        Returns:
            Dictionary containing social media activity data
        """
        # This would typically connect to social media APIs to get actual data
        # For now, we'll simulate by looking at social media draft files
        pending_approval_path = Path(config.vault_path) / "Pending_Approval"

        social_activity = {
            'period': {'from': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                      'to': datetime.now().strftime('%Y-%m-%d')},
            'twitter_drafts': 0,
            'facebook_drafts': 0,
            'instagram_drafts': 0,
            'total_drafts': 0,
            'posted_content': []  # This would come from actual social media APIs
        }

        if pending_approval_path.exists():
            seven_days_ago = datetime.now() - timedelta(days=7)

            for file_path in pending_approval_path.iterdir():
                if file_path.is_file():
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mod_time >= seven_days_ago:
                        filename = file_path.name.lower()

                        if 'twitter' in filename:
                            social_activity['twitter_drafts'] += 1
                        elif 'facebook' in filename or 'fb_' in filename:
                            social_activity['facebook_drafts'] += 1
                        elif 'instagram' in filename or 'ig_' in filename or 'insta_' in filename:
                            social_activity['instagram_drafts'] += 1

                        social_activity['total_drafts'] += 1

        logger.info(f"Found social media activity: {social_activity['total_drafts']} drafts in last 7 days")
        return social_activity

    def generate_audit_report(self) -> str:
        """
        Generate a comprehensive audit report.

        Returns:
            Formatted audit report as string
        """
        logger.info("Starting weekly audit report generation")

        # Get data for the report
        done_files = self.get_done_files_last_week()
        odoo_data = self.get_odoo_financial_data_last_week()
        social_data = self.get_social_media_activity_last_week()

        # Generate the report
        report_date = datetime.now().strftime('%Y-%m-%d')
        report = f"""
# Weekly Business Audit Report
Generated on: {report_date}

## Executive Summary
This report summarizes business activities for the week ending {datetime.now().strftime('%Y-%m-%d')}.

## 1. Task Completion Summary
- Total completed tasks: {len(done_files)}
- Tasks completed during the week:

"""
        for file_path in done_files:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            report += f"  - {mod_time.strftime('%Y-%m-%d %H:%M')} - {file_path.name}\n"

        # Safely access Odoo financial data
        period_from = odoo_data.get('period', {}).get('from', 'N/A') if isinstance(odoo_data.get('period'), dict) else 'N/A'
        period_to = odoo_data.get('period', {}).get('to', 'N/A') if isinstance(odoo_data.get('period'), dict) else 'N/A'
        transaction_count = odoo_data.get('metrics', {}).get('transaction_count', 0) if isinstance(odoo_data.get('metrics'), dict) else 0
        total_revenue = odoo_data.get('metrics', {}).get('total_revenue', 0) if isinstance(odoo_data.get('metrics'), dict) else 0
        avg_transaction_value = odoo_data.get('metrics', {}).get('average_transaction_value', 0) if isinstance(odoo_data.get('metrics'), dict) else 0

        report += f"""

## 2. Financial Performance
- Period: {period_from} to {period_to}
- Total Transactions: {transaction_count}
- Total Revenue: ${total_revenue:,.2f}
- Average Transaction Value: ${avg_transaction_value:,.2f}

### Transaction Details:
"""
        # Safely iterate through transactions
        transactions = odoo_data.get('transactions', [])
        if isinstance(transactions, list):
            for transaction in transactions:
                if isinstance(transaction, dict):
                    date = transaction.get('date', 'N/A')
                    name = transaction.get('name', 'N/A')
                    amount = transaction.get('amount', transaction.get('total_amount', 0))
                    report += f"  - {date}: {name} (${amount:,.2f})\n"
                else:
                    logger.warning(f"Skipping non-dict transaction: {transaction}")
        else:
            logger.warning(f"Transactions is not a list: {type(transactions)}")

        report += f"""

## 3. Social Media Activity
- Period: {social_data['period']['from']} to {social_data['period']['to']}
- Twitter Drafts: {social_data['twitter_drafts']}
- Facebook Drafts: {social_data['facebook_drafts']}
- Instagram Drafts: {social_data['instagram_drafts']}
- Total Drafts: {social_data['total_drafts']}

## 4. Key Metrics & Insights
- Task completion rate: {len(done_files)} tasks completed
- Revenue growth: ${total_revenue:,.2f} generated
- Content pipeline: {social_data['total_drafts']} social media drafts prepared

## 5. Recommendations
- Continue current task processing cadence
- Monitor social media engagement on posted content
- Review high-value transactions for follow-up opportunities

"""
        logger.info("Weekly audit report generated successfully")
        return report.strip()

    def save_audit_report(self, report_content: str) -> Optional[Path]:
        """
        Save the audit report as AUDIT_YYYYMMDD.md in the vault.

        Args:
            report_content: Content of the audit report

        Returns:
            Path to the saved report file, or None if failed
        """
        try:
            # Generate filename with current date
            date_str = datetime.now().strftime('%Y%m%d')
            filename = f"AUDIT_{date_str}.md"

            # Save to vault root
            report_path = Path(config.vault_path) / filename

            # Write the report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            logger.info(f"Weekly audit report saved to: {report_path}")
            audit_logger.log_external_action("report_saved", "weekly_audit", True, {"file": filename})

            return report_path

        except Exception as e:
            logger.error(f"Error saving audit report: {e}")
            audit_logger.log_external_action("report_save_error", "weekly_audit", False, {"error": str(e)})
            return None

    def run_audit(self) -> bool:
        """
        Run the complete weekly audit process.

        Returns:
            True if successful, False otherwise
        """
        logger.info("Starting weekly audit process")

        try:
            # Generate the audit report
            report_content = self.generate_audit_report()

            if not report_content:
                logger.error("Failed to generate audit report content")
                return False

            # Save the report
            report_path = self.save_audit_report(report_content)

            if not report_path:
                logger.error("Failed to save audit report")
                return False

            # Feed data into Monday CEO Briefing (if applicable)
            self.feed_to_ceo_briefing(report_content, report_path)

            logger.info("Weekly audit completed successfully")
            audit_logger.log_external_action("audit_completed", "weekly_audit", True, {"report": report_path.name})

            return True

        except Exception as e:
            logger.error(f"Error running weekly audit: {e}")
            audit_logger.log_external_action("audit_error", "weekly_audit", False, {"error": str(e)})
            return False

    def feed_to_ceo_briefing(self, report_content: str, report_path: Path):
        """
        Feed the audit data into Monday CEO Briefing.

        Args:
            report_content: Content of the audit report
            report_path: Path to the saved report file
        """
        try:
            # This would typically integrate with the CEO Briefing system
            # For now, we'll just log that the integration would happen
            logger.info("Feeding audit data to CEO Briefing system")

            # In a real implementation, this would:
            # 1. Extract key metrics from the report
            # 2. Update the CEO_Briefing file with the new data
            # 3. Possibly send a notification

            # For demonstration, we'll just add a reference to the audit report in the dashboard
            try:
                from dashboard_updater import DashboardUpdater
                dashboard_updater = DashboardUpdater(config.vault_path)
                dashboard_updater.update_dashboard()
            except ImportError as e:
                logger.warning(f"Could not import DashboardUpdater: {e}")
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")

            # Also try to update the CEO briefing if available
            try:
                from ceo_briefing import CEOBriefing
                ceo_briefing = CEOBriefing(vault_path=config.vault_path)
                ceo_briefing.generate_briefing()
                logger.info("CEO Briefing updated successfully")
            except ImportError as e:
                logger.warning(f"Could not import CEO Briefing: {e}")
            except Exception as e:
                logger.error(f"Error updating CEO Briefing: {e}")

            audit_logger.log_external_action("ceo_briefing_updated", "weekly_audit", True, {
                "report": report_path.name,
                "integration": "dashboard_updated"
            })

        except Exception as e:
            logger.error(f"Error feeding data to CEO Briefing: {e}")
            audit_logger.log_external_action("ceo_briefing_error", "weekly_audit", False, {"error": str(e)})

    def start_scheduler(self):
        """
        Start the scheduler to run the audit every Sunday night.
        """
        # Schedule the audit to run every Sunday at 11:59 PM
        schedule.every().sunday.at("23:59").do(self.run_audit)

        logger.info("Weekly audit scheduler started. Will run every Sunday at 23:59.")
        audit_logger.log_external_action("scheduler_started", "weekly_audit", True, {
            "schedule": "every Sunday at 23:59"
        })

        # Keep the scheduler running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


def main():
    """Main function to run the weekly audit."""
    try:
        audit = WeeklyAudit()

        # Option 1: Run the audit immediately (for testing)
        # Uncomment the next line to run the audit now
        # audit.run_audit()

        # Option 2: Start the scheduler to run weekly
        print("Starting weekly audit scheduler. The audit will run every Sunday at 23:59.")
        print("Press Ctrl+C to stop the scheduler.")
        try:
            audit.start_scheduler()
        except KeyboardInterrupt:
            print("\nScheduler stopped.")
        except Exception as e:
            logger.error(f"Error in weekly audit scheduler: {e}")
            audit_logger.log_external_action("weekly_audit_scheduler_error", "audit", False, {"error": str(e)})
            raise
    except Exception as e:
        logger.error(f"Error in weekly audit main: {e}")
        audit_logger.log_external_action("weekly_audit_main_error", "audit", False, {"error": str(e)})
        raise


if __name__ == "__main__":
    main()
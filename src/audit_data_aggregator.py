'''
Audit data aggregator for the Personal AI Employee system.
Collects data from multiple sources for the weekly audit report.
'''

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger, AuditLogger
    from .config import get_config
    from .file_utils import get_file_utils
    from .odoo_integration import OdooIntegration
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger, AuditLogger
    from config import get_config
    from file_utils import get_file_utils
    from odoo_integration import OdooIntegration

logger = setup_logger('audit_data_aggregator')
audit_logger = AuditLogger('audit_data_aggregator')
config = get_config()
file_utils = get_file_utils()
odoo_integration = OdooIntegration()

class AuditDataAggregator:
    """
    Audit data aggregator for the Personal AI Employee system.
    Collects data from multiple sources for the weekly audit report.
    """

    def __init__(self):
        """Initialize the audit data aggregator."""
        pass

    def collect_done_files_data(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Collect data about files in the Done folder from the past N days.

        Args:
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary containing done files data
        """
        done_path = Path(config.vault_path) / "Done"
        if not done_path.exists():
            logger.warning(f"Done folder does not exist: {done_path}")
            return {'count': 0, 'files': [], 'by_date': {}}

        files = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        for file_path in done_path.iterdir():
            if file_path.is_file():
                # Get file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

                if mod_time >= cutoff_date:
                    file_info = {
                        'name': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'modified': mod_time.isoformat(),
                        'date': mod_time.strftime('%Y-%m-%d')
                    }
                    files.append(file_info)

        # Organize by date
        by_date = {}
        for file_info in files:
            date = file_info['date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(file_info)

        logger.info(f"Collected {len(files)} done files from the last {days_back} days")
        return {
            'count': len(files),
            'files': files,
            'by_date': by_date,
            'period': {
                'start': cutoff_date.strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d')
            }
        }

    def collect_odoo_financial_data(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Collect financial data from Odoo from the past N days.

        Args:
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary containing Odoo financial data
        """
        # Calculate date range
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        # Get transactions from Odoo
        transactions = odoo_integration.read_transactions(date_from, date_to)

        # Calculate financial metrics
        total_revenue = sum(t['total_amount'] for t in transactions)
        total_subtotal = sum(t['subtotal'] for t in transactions)
        transaction_count = len(transactions)
        avg_transaction_value = total_revenue / transaction_count if transaction_count > 0 else 0

        # Organize by customer
        by_customer = {}
        for transaction in transactions:
            customer = transaction['customer']
            if customer not in by_customer:
                by_customer[customer] = []
            by_customer[customer].append(transaction)

        # Organize by date
        by_date = {}
        for transaction in transactions:
            date = transaction['date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(transaction)

        financial_data = {
            'transactions': transactions,
            'metrics': {
                'total_revenue': total_revenue,
                'total_subtotal': total_subtotal,
                'transaction_count': transaction_count,
                'average_transaction_value': avg_transaction_value
            },
            'by_customer': by_customer,
            'by_date': by_date,
            'period': {
                'start': date_from,
                'end': date_to
            }
        }

        logger.info(f"Collected financial data from Odoo: {transaction_count} transactions")
        return financial_data

    def collect_social_media_activity(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Collect social media activity data from the past N days.

        Args:
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary containing social media activity data
        """
        pending_approval_path = Path(config.vault_path) / "Pending_Approval"
        approved_path = Path(config.vault_path) / "Approved"
        done_path = Path(config.vault_path) / "Done"

        activity_data = {
            'drafts': {
                'twitter': [],
                'facebook': [],
                'instagram': [],
                'total': 0
            },
            'posted': {
                'twitter': [],
                'facebook': [],
                'instagram': [],
                'total': 0
            },
            'period': {
                'start': (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d'),
                'end': datetime.now().strftime('%Y-%m-%d')
            }
        }

        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Look for social media related files in different folders
        for folder_path, activity_type in [(pending_approval_path, 'drafts'), (done_path, 'posted')]:
            if folder_path.exists():
                for file_path in folder_path.iterdir():
                    if file_path.is_file():
                        # Get file modification time
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)

                        if mod_time >= cutoff_date:
                            filename = file_path.name.lower()

                            # Classify based on filename
                            if 'twitter' in filename or 'tweet' in filename:
                                activity_data[activity_type]['twitter'].append({
                                    'name': file_path.name,
                                    'date': mod_time.isoformat()
                                })
                                activity_data[activity_type]['total'] += 1
                            elif 'facebook' in filename or 'fb_' in filename:
                                activity_data[activity_type]['facebook'].append({
                                    'name': file_path.name,
                                    'date': mod_time.isoformat()
                                })
                                activity_data[activity_type]['total'] += 1
                            elif 'instagram' in filename or 'ig_' in filename or 'insta_' in filename:
                                activity_data[activity_type]['instagram'].append({
                                    'name': file_path.name,
                                    'date': mod_time.isoformat()
                                })
                                activity_data[activity_type]['total'] += 1

        logger.info(f"Collected social media activity: {activity_data['drafts']['total']} drafts, {activity_data['posted']['total']} posted")
        return activity_data

    def aggregate_all_data(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Aggregate all audit data from multiple sources.

        Args:
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary containing all aggregated audit data
        """
        logger.info(f"Starting audit data aggregation for last {days_back} days")

        # Collect all data sources
        done_files_data = self.collect_done_files_data(days_back)
        odoo_financial_data = self.collect_odoo_financial_data(days_back)
        social_media_data = self.collect_social_media_activity(days_back)

        # Create aggregated report
        aggregated_data = {
            'summary': {
                'period': {
                    'start': min(
                        done_files_data['period']['start'],
                        odoo_financial_data['period']['start'],
                        social_media_data['period']['start']
                    ),
                    'end': datetime.now().strftime('%Y-%m-%d')
                },
                'total_completed_tasks': done_files_data['count'],
                'total_transactions': odoo_financial_data['metrics']['transaction_count'],
                'total_revenue': odoo_financial_data['metrics']['total_revenue'],
                'total_drafts': social_media_data['drafts']['total'],
                'total_posted': social_media_data['posted']['total']
            },
            'done_files': done_files_data,
            'financial_data': odoo_financial_data,
            'social_media': social_media_data,
            'generated_at': datetime.now().isoformat()
        }

        logger.info("Audit data aggregation completed successfully")
        audit_logger.log_external_action("data_aggregated", "audit", True, {
            "period_days": days_back,
            "tasks_completed": aggregated_data['summary']['total_completed_tasks'],
            "transactions": aggregated_data['summary']['total_transactions']
        })

        return aggregated_data

    def generate_executive_summary(self, aggregated_data: Dict[str, Any]) -> str:
        """
        Generate an executive summary from the aggregated data.

        Args:
            aggregated_data: Dictionary containing all aggregated audit data

        Returns:
            Executive summary as a string
        """
        summary = aggregated_data['summary']

        exec_summary = f"""
# Executive Summary - Weekly Business Audit
Period: {summary['period']['start']} to {summary['period']['end']}

## Key Performance Indicators
- Tasks Completed: {summary['total_completed_tasks']:,}
- Revenue Generated: ${summary['total_revenue']:,.2f}
- Sales Transactions: {summary['total_transactions']:,}
- Social Media Drafts: {summary['total_drafts']:,}
- Social Media Posted: {summary['total_posted']:,}

## Performance Highlights
- Average Transaction Value: ${summary['total_revenue']/summary['total_transactions'] if summary['total_transactions'] > 0 else 0:,.2f}
- Task Completion Rate: {summary['total_completed_tasks']} tasks completed
- Revenue per Transaction: ${summary['total_revenue']/summary['total_transactions'] if summary['total_transactions'] > 0 else 0:,.2f}

## Areas of Focus
- Review high-value transactions for follow-up
- Monitor social media engagement metrics
- Analyze task completion patterns for optimization

"""
        return exec_summary.strip()

    def save_aggregated_data(self, aggregated_data: Dict[str, Any], filepath: str = None) -> bool:
        """
        Save the aggregated data to a JSON file.

        Args:
            aggregated_data: Dictionary containing all aggregated audit data
            filepath: Path to save the data (default: auto-generated with timestamp)

        Returns:
            True if successful, False otherwise
        """
        if not filepath:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"{config.vault_path}/AUDIT_DATA_{date_str}.json"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(aggregated_data, f, indent=2, default=str)

            logger.info(f"Aggregated audit data saved to: {filepath}")
            audit_logger.log_external_action("data_saved", "audit", True, {"file": filepath})
            return True

        except Exception as e:
            logger.error(f"Error saving aggregated data: {e}")
            audit_logger.log_external_action("data_save_error", "audit", False, {"error": str(e)})
            return False

    def load_aggregated_data(self, filepath: str) -> Dict[str, Any]:
        """
        Load aggregated data from a JSON file.

        Args:
            filepath: Path to the saved data file

        Returns:
            Dictionary containing the loaded audit data, or empty dict if failed
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            logger.info(f"Aggregated audit data loaded from: {filepath}")
            return data

        except Exception as e:
            logger.error(f"Error loading aggregated data: {e}")
            return {}


# Global audit data aggregator instance
audit_data_aggregator = AuditDataAggregator()


def get_audit_data_aggregator() -> AuditDataAggregator:
    """Get the global audit data aggregator instance."""
    return audit_data_aggregator


def main():
    """Main function to demonstrate audit data aggregator usage."""
    aggregator = get_audit_data_aggregator()

    # Example: Aggregate data for the last 7 days
    print("Collecting and aggregating audit data for the last 7 days...")
    aggregated_data = aggregator.aggregate_all_data(days_back=7)

    # Generate executive summary
    exec_summary = aggregator.generate_executive_summary(aggregated_data)
    print("\nExecutive Summary:")
    print(exec_summary)

    # Save the data
    success = aggregator.save_aggregated_data(aggregated_data)
    if success:
        print("\nAggregated data saved successfully!")
    else:
        print("\nFailed to save aggregated data.")


if __name__ == "__main__":
    main()
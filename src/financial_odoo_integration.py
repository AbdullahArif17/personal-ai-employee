import os
import sys
import xmlrpc.client
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

class OdooIntegration:
    def __init__(self):
        self.url = os.getenv('ODOO_URL', 'http://localhost:8069')
        self.database = os.getenv('ODOO_DATABASE', 'personal_empolyee')
        self.username = os.getenv('ODOO_USERNAME', 'abdullaharif893@gmail.com')
        self.password = os.getenv('ODOO_PASSWORD', 'admin123')
        self.uid = None
        self.models = None
        self.common = None

    def connect(self):
        """Establish connection to Odoo instance."""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.database, self.username, self.password, {})

            if not self.uid:
                raise Exception("Authentication failed")

            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
            return True
        except Exception as e:
            print(f"ERROR: Could not connect to Odoo: {e}")
            return False

    def test_connection(self) -> tuple[bool, str]:
        """Test if Odoo is reachable."""
        try:
            if self.connect():
                return True, "Successfully connected to Odoo"
            else:
                return False, "Failed to connect to Odoo"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def get_invoices(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Read account.move records where move_type in ['out_invoice', 'in_invoice']."""
        try:
            if not self.models or not self.uid:
                self.connect()

            # Search for invoices (both customer and vendor)
            invoice_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'search',
                [[['move_type', 'in', ['out_invoice', 'in_invoice']], ['state', '!=', 'cancel']]],
                {'limit': limit, 'order': 'date desc'}
            )

            # Read invoice details
            invoices = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'read',
                [invoice_ids],
                {'fields': ['name', 'date', 'amount_total', 'state', 'partner_id', 'move_type']}
            )

            # Format the data
            formatted_invoices = []
            for inv in invoices:
                formatted_invoices.append({
                    'name': inv['name'],
                    'date': inv['date'],
                    'amount_total': inv['amount_total'],
                    'state': inv['state'],
                    'partner_id': inv['partner_id'][1] if inv['partner_id'] else None,  # Get partner name
                    'move_type': inv['move_type']
                })

            return formatted_invoices
        except Exception as e:
            print(f"ERROR: Could not fetch invoices: {e}")
            return []

    def get_expenses(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Read account.move records where move_type = 'in_invoice'."""
        try:
            if not self.models or not self.uid:
                self.connect()

            # Search for expenses (vendor bills)
            expense_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'search',
                [[['move_type', '=', 'in_invoice'], ['state', '!=', 'cancel']]],
                {'limit': limit, 'order': 'date desc'}
            )

            # Read expense details
            expenses = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'read',
                [expense_ids],
                {'fields': ['name', 'date', 'amount_total', 'partner_id']}
            )

            # Format the data
            formatted_expenses = []
            for exp in expenses:
                formatted_expenses.append({
                    'name': exp['name'],
                    'date': exp['date'],
                    'amount_total': exp['amount_total'],
                    'partner_id': exp['partner_id'][1] if exp['partner_id'] else None,  # Get partner name
                })

            return formatted_expenses
        except Exception as e:
            print(f"ERROR: Could not fetch expenses: {e}")
            return []

    def get_financial_summary(self) -> Dict[str, Any]:
        """Return financial summary data."""
        try:
            if not self.models or not self.uid:
                self.connect()

            # Calculate date for last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            # Get total invoiced (out invoices)
            total_invoiced_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'search',
                [[['move_type', '=', 'out_invoice'], ['state', '!=', 'cancel'], ['date', '>=', thirty_days_ago]]],
                {}
            )

            total_invoiced_records = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'read',
                [total_invoiced_ids],
                {'fields': ['amount_total']}
            )

            total_invoiced = sum(record['amount_total'] or 0 for record in total_invoiced_records)

            # Get total expenses (in invoices)
            total_expense_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'search',
                [[['move_type', '=', 'in_invoice'], ['state', '!=', 'cancel'], ['date', '>=', thirty_days_ago]]],
                {}
            )

            total_expense_records = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'read',
                [total_expense_ids],
                {'fields': ['amount_total']}
            )

            total_expenses = sum(record['amount_total'] or 0 for record in total_expense_records)

            # Get outstanding payments (unpaid invoices)
            outstanding_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'search',
                [[['move_type', '=', 'out_invoice'], ['state', '=', 'posted'], ['payment_state', '!=', 'paid']]],
                {}
            )

            outstanding_records = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.move',
                'read',
                [outstanding_ids],
                {'fields': ['amount_total']}
            )

            outstanding_payments = sum(record['amount_total'] or 0 for record in outstanding_records)

            return {
                'total_invoiced': total_invoiced,
                'total_expenses': total_expenses,
                'outstanding_payments': outstanding_payments,
                'currency': 'USD',  # Default, could be retrieved from company settings
                'period': 'Last 30 days',
                'report_date': datetime.now().strftime('%Y-%m-%d')
            }
        except Exception as e:
            print(f"ERROR: Could not fetch financial summary: {e}")
            return {
                'total_invoiced': 0,
                'total_expenses': 0,
                'outstanding_payments': 0,
                'currency': 'USD',
                'period': 'Last 30 days',
                'report_date': datetime.now().strftime('%Y-%m-%d'),
                'error': str(e)
            }

    def get_transactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Read account.payment records."""
        try:
            if not self.models or not self.uid:
                self.connect()

            # Search for payments
            payment_ids = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.payment',
                'search',
                [[['state', '!=', 'draft']]],  # Exclude draft payments
                {'limit': limit, 'order': 'date desc'}
            )

            # Read payment details
            payments = self.models.execute_kw(
                self.database,
                self.uid,
                self.password,
                'account.payment',
                'read',
                [payment_ids],
                {'fields': ['name', 'date', 'amount', 'payment_type', 'state', 'partner_id']}
            )

            # Format the data
            formatted_payments = []
            for pay in payments:
                formatted_payments.append({
                    'name': pay['name'],
                    'date': pay['date'],
                    'amount': pay['amount'],
                    'payment_type': pay['payment_type'],
                    'state': pay['state'],
                    'partner_id': pay['partner_id'][1] if pay['partner_id'] else None,  # Get partner name
                })

            return formatted_payments
        except Exception as e:
            print(f"ERROR: Could not fetch transactions: {e}")
            return []


# Example usage
if __name__ == "__main__":
    odoo = OdooIntegration()
    success, message = odoo.test_connection()
    print(message)
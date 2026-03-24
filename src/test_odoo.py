import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_odoo_integration import OdooIntegration

def main():
    print("Testing Odoo Integration...")

    # Create Odoo integration instance
    odoo = OdooIntegration()

    # Test connection
    success, message = odoo.test_connection()
    print(f"Connection Test: {message}")

    if not success:
        print("Cannot proceed with tests - connection failed.")
        return

    print("\n--- Testing Financial Summary ---")
    summary = odoo.get_financial_summary()
    print(f"Financial Summary: {summary}")

    print("\n--- Testing Invoices ---")
    invoices = odoo.get_invoices(limit=5)
    print(f"Found {len(invoices)} invoices:")
    for invoice in invoices:
        print(f"  - {invoice['name']} | Date: {invoice['date']} | Amount: {invoice['amount_total']} | Partner: {invoice['partner_id']}")

    print("\n--- Testing Expenses ---")
    expenses = odoo.get_expenses(limit=5)
    print(f"Found {len(expenses)} expenses:")
    for expense in expenses:
        print(f"  - {expense['name']} | Date: {expense['date']} | Amount: {expense['amount_total']} | Partner: {expense['partner_id']}")

    print("\n--- Testing Transactions ---")
    transactions = odoo.get_transactions(limit=5)
    print(f"Found {len(transactions)} transactions:")
    for transaction in transactions:
        print(f"  - {transaction['name']} | Date: {transaction['date']} | Amount: {transaction['amount']} | Type: {transaction['payment_type']} | State: {transaction['state']}")

if __name__ == "__main__":
    main()
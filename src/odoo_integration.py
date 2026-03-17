'''
Odoo integration for the Personal AI Employee system.
Connects to local Odoo Community instance and manages invoice creation and financial reporting.
'''

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger, AuditLogger
    from .config import get_config
    from .file_utils import get_file_utils
    from .rate_limiter import get_rate_limiter
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger, AuditLogger
    from config import get_config
    from file_utils import get_file_utils
    from rate_limiter import get_rate_limiter

logger = setup_logger('odoo_integration')
audit_logger = AuditLogger('odoo_integration')
config = get_config()
file_utils = get_file_utils()
rate_limiter = get_rate_limiter()

class OdooIntegration:
    """
    Odoo integration implementation for the Personal AI Employee system.
    Connects to local Odoo Community instance and manages invoice creation and financial reporting.
    """

    def __init__(self):
        """Initialize the Odoo integration."""
        # Import Odoo libraries
        try:
            from odoo_rpc import ODOO
            self.odoo_lib = ODOO
        except ImportError:
            logger.error("odoo-rpc library not installed. Please install it with: pip install odoo-rpc")
            self.odoo_lib = None

    def connect_to_odoo(self):
        """
        Connect to the Odoo instance using credentials from config.

        Returns:
            Odoo connection object, or None if connection fails
        """
        if not self.odoo_lib:
            logger.error("Cannot connect to Odoo: odoo-rpc library not available")
            return None

        try:
            # Get Odoo credentials
            url = config.odoo_url
            db = config.odoo_db
            username = config.odoo_username
            password = config.odoo_password

            if not all([url, db, username, password]):
                logger.error("Missing required Odoo API credentials")
                return None

            # Connect to Odoo
            odoo = self.odoo_lib(url, port=80, database=db, user=username, password=password)

            # Test connection
            user_info = odoo.res_users.read([odoo.uid], ['name', 'login'])
            if user_info:
                logger.info(f"Successfully connected to Odoo as user: {user_info[0]['name']}")
                audit_logger.log_external_action("connection_success", "odoo", True, {"user": user_info[0]['name']})
                return odoo
            else:
                logger.error("Failed to verify Odoo connection")
                return None

        except Exception as e:
            logger.error(f"Error connecting to Odoo: {e}")
            audit_logger.log_external_action("connection_error", "odoo", False, {"error": str(e)})
            return None

    def create_invoice_draft(self, invoice_data: Dict[str, Any]) -> Optional[Path]:
        """
        Create an invoice draft file for approval.

        Args:
            invoice_data: Dictionary containing invoice information

        Returns:
            Path to the created draft file, or None if failed
        """
        try:
            # Convert invoice data to a readable format
            invoice_text = f"""
# Odoo Invoice Request

## Customer Information
- Name: {invoice_data.get('customer_name', 'Not specified')}
- Email: {invoice_data.get('customer_email', 'Not specified')}
- Phone: {invoice_data.get('customer_phone', 'Not specified')}

## Invoice Details
- Date: {datetime.now().strftime('%Y-%m-%d')}
- Reference: {invoice_data.get('reference', 'AUTO-' + datetime.now().strftime('%Y%m%d%H%M%S'))}

## Line Items
"""
            for i, item in enumerate(invoice_data.get('line_items', [])):
                invoice_text += f"- Item {i+1}: {item.get('name', 'Unnamed')} - Quantity: {item.get('quantity', 1)}, Price: {item.get('price_unit', 0)}\n"

            invoice_text += f"\n## Totals\n"
            invoice_text += f"- Subtotal: {invoice_data.get('subtotal', 'Calculated automatically')}\n"
            invoice_text += f"- Tax: {invoice_data.get('tax_amount', 'Calculated automatically')}\n"
            invoice_text += f"- Total: {invoice_data.get('total_amount', 'Calculated automatically')}\n"

            invoice_text += f"\n## Notes\n"
            invoice_text += f"{invoice_data.get('notes', 'No additional notes')}\n"

            # Create draft file in Pending_Approval folder
            draft_path = file_utils.create_draft_file(
                content=invoice_text,
                folder="Pending_Approval",
                prefix="odoo_invoice"
            )

            if draft_path:
                logger.info(f"Created Odoo invoice draft: {draft_path.name}")
                audit_logger.log_external_action("invoice_draft_created", "odoo", True, {"file": draft_path.name})
                return draft_path
            else:
                logger.error("Failed to create Odoo invoice draft file")
                return None

        except Exception as e:
            logger.error(f"Error creating Odoo invoice draft: {e}")
            return None

    def create_invoice_from_draft(self, file_path: Path) -> Optional[int]:
        """
        Create an invoice in Odoo from an approved draft file.

        Args:
            file_path: Path to the approved invoice draft file

        Returns:
            Invoice ID if successful, None otherwise
        """
        try:
            # Check rate limit before creating invoice
            if not rate_limiter.increment_usage('odoo'):
                logger.warning("Odoo invoice creation rate limit exceeded")
                audit_logger.log_rate_limit_event('odoo', 'invoices', *rate_limiter.get_usage('odoo'))
                return None

            if config.dry_run:
                logger.info(f"(DRY RUN) Would create invoice from draft: {file_path.name}")
                audit_logger.log_external_action("invoice_dry_run", "odoo", True, {"file": file_path.name})
                return 12345  # Return a dummy ID for dry run

            # Connect to Odoo
            odoo = self.connect_to_odoo()
            if not odoo:
                logger.error("Cannot create invoice: Failed to connect to Odoo")
                return None

            # Read the draft content
            content = file_utils.read_file_content(file_path)
            if not content:
                logger.error(f"Could not read content from invoice draft: {file_path.name}")
                return None

            # Parse the invoice data from the draft file
            invoice_data = self._parse_invoice_from_draft(content)

            if not invoice_data:
                logger.error(f"Could not parse invoice data from draft: {file_path.name}")
                return None

            # Search for or create the customer (partner)
            partner_name = invoice_data.get('customer_name', 'Unknown Customer')
            partner_ids = odoo.res_partner.search([('name', '=', partner_name)])

            if not partner_ids:
                # Create new partner
                partner_id = odoo.res_partner.create({
                    'name': partner_name,
                    'email': invoice_data.get('customer_email', ''),
                    'phone': invoice_data.get('customer_phone', ''),
                    'customer_rank': 1,  # Mark as customer
                })
                logger.info(f"Created new customer: {partner_name}")
            else:
                partner_id = partner_ids[0]
                logger.info(f"Using existing customer: {partner_name}")

            # Prepare invoice line items
            invoice_lines = []
            for item in invoice_data.get('line_items', []):
                # Search for or create product
                product_name = item.get('name', 'Service')
                product_ids = odoo.product_product.search([('name', '=', product_name)])

                if not product_ids:
                    # Create new service product
                    product_id = odoo.product_product.create({
                        'name': product_name,
                        'type': 'service',  # Use 'service' for services
                        'list_price': item.get('price_unit', 0),
                        'sale_ok': True,
                    })
                    logger.info(f"Created new product: {product_name}")
                else:
                    product_id = product_ids[0]
                    logger.info(f"Using existing product: {product_name}")

                # Add line to invoice
                invoice_lines.append((0, 0, {
                    'product_id': product_id,
                    'name': item.get('description', product_name),
                    'quantity': item.get('quantity', 1),
                    'price_unit': item.get('price_unit', 0),
                }))

            # Create the invoice
            invoice_id = odoo.account_move.create({
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # 'out_invoice' for customer invoices
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'ref': invoice_data.get('reference', ''),
                'invoice_line_ids': invoice_lines,
                'narration': invoice_data.get('notes', ''),
            })

            # Validate and post the invoice
            odoo.account_move.action_post([invoice_id])

            logger.info(f"Successfully created and posted invoice in Odoo with ID: {invoice_id}")
            audit_logger.log_external_action("invoice_created", "odoo", True, {"invoice_id": invoice_id})

            return invoice_id

        except Exception as e:
            logger.error(f"Error creating invoice from draft {file_path.name}: {e}")
            audit_logger.log_external_action("invoice_error", "odoo", False, {
                "file": file_path.name,
                "error": str(e)
            })
            return None

    def _parse_invoice_from_draft(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Parse invoice information from a draft file.

        Args:
            content: Content of the draft file

        Returns:
            Dictionary containing parsed invoice data, or None if parsing fails
        """
        try:
            lines = content.split('\n')
            invoice_data = {
                'customer_name': '',
                'customer_email': '',
                'customer_phone': '',
                'reference': '',
                'line_items': [],
                'notes': ''
            }

            current_section = None
            for line in lines:
                line = line.strip()

                # Detect section headers
                if line.startswith('## Customer Information'):
                    current_section = 'customer'
                elif line.startswith('## Invoice Details'):
                    current_section = 'details'
                elif line.startswith('## Line Items'):
                    current_section = 'items'
                elif line.startswith('## Notes'):
                    current_section = 'notes'

                # Parse customer info
                elif current_section == 'customer' and line.startswith('- Name:'):
                    invoice_data['customer_name'] = line.replace('- Name:', '').strip()
                elif current_section == 'customer' and line.startswith('- Email:'):
                    invoice_data['customer_email'] = line.replace('- Email:', '').strip()
                elif current_section == 'customer' and line.startswith('- Phone:'):
                    invoice_data['customer_phone'] = line.replace('- Phone:', '').strip()

                # Parse invoice details
                elif current_section == 'details' and line.startswith('- Reference:'):
                    invoice_data['reference'] = line.replace('- Reference:', '').strip()

                # Parse line items
                elif current_section == 'items' and line.startswith('- Item'):
                    # Extract item details from the line
                    # Format: "- Item X: name - Quantity: Y, Price: Z"
                    import re
                    match = re.search(r'Item \d+: ([^-\n]+) - Quantity: ([\d.]+), Price: ([\d.]+)', line)
                    if match:
                        item_name = match.group(1).strip()
                        quantity = float(match.group(2))
                        price = float(match.group(3))

                        invoice_data['line_items'].append({
                            'name': item_name,
                            'quantity': quantity,
                            'price_unit': price
                        })

                # Parse notes
                elif current_section == 'notes' and not line.startswith('##'):
                    if invoice_data['notes']:
                        invoice_data['notes'] += ' ' + line
                    else:
                        invoice_data['notes'] = line

            # Validate that we have essential data
            if not invoice_data['customer_name'] or not invoice_data['line_items']:
                logger.warning("Parsed invoice data missing essential information")
                return None

            return invoice_data

        except Exception as e:
            logger.error(f"Error parsing invoice from draft: {e}")
            return None

    def read_transactions(self, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """
        Read transactions from Odoo within a date range.

        Args:
            date_from: Start date in YYYY-MM-DD format (default: last 7 days)
            date_to: End date in YYYY-MM-DD format (default: today)

        Returns:
            List of transaction dictionaries
        """
        try:
            # Connect to Odoo
            odoo = self.connect_to_odoo()
            if not odoo:
                logger.error("Cannot read transactions: Failed to connect to Odoo")
                return []

            # Set default date range to last 7 days if not specified
            if not date_from:
                from datetime import timedelta
                date_from_obj = datetime.now() - timedelta(days=7)
                date_from = date_from_obj.strftime('%Y-%m-%d')

            if not date_to:
                date_to = datetime.now().strftime('%Y-%m-%d')

            # Search for invoices within the date range
            invoice_ids = odoo.account_move.search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', date_from),
                ('invoice_date', '<=', date_to),
                ('state', '!=', 'cancel')
            ])

            transactions = []
            for inv_id in invoice_ids:
                invoice = odoo.account_move.read([inv_id], [
                    'name', 'ref', 'invoice_date', 'amount_total',
                    'amount_untaxed', 'partner_id', 'state'
                ])[0]

                # Get partner name
                partner_name = ""
                if invoice['partner_id']:
                    partner = odoo.res_partner.read([invoice['partner_id'][0]], ['name'])[0]
                    partner_name = partner['name']

                transaction = {
                    'id': inv_id,
                    'name': invoice['name'],
                    'reference': invoice['ref'],
                    'date': str(invoice['invoice_date']),
                    'total_amount': invoice['amount_total'],
                    'subtotal': invoice['amount_untaxed'],
                    'customer': partner_name,
                    'state': invoice['state']
                }
                transactions.append(transaction)

            logger.info(f"Retrieved {len(transactions)} transactions from Odoo")
            return transactions

        except Exception as e:
            logger.error(f"Error reading transactions from Odoo: {e}")
            return []

    def generate_report(self, date_from: str = None, date_to: str = None) -> str:
        """
        Generate a financial report from Odoo transactions.

        Args:
            date_from: Start date in YYYY-MM-DD format (default: last 7 days)
            date_to: End date in YYYY-MM-DD format (default: today)

        Returns:
            Formatted report as string
        """
        try:
            transactions = self.read_transactions(date_from, date_to)

            if not transactions:
                return "No transactions found for the specified period."

            # Calculate totals
            total_revenue = sum(t['total_amount'] for t in transactions)
            total_subtotal = sum(t['subtotal'] for t in transactions)
            transaction_count = len(transactions)

            # Generate report
            report = f"""
# Financial Report
Period: {date_from or 'Last 7 Days'} to {date_to or 'Today'}

## Summary
- Total Transactions: {transaction_count}
- Total Revenue: ${total_revenue:,.2f}
- Total Subtotal: ${total_subtotal:,.2f}

## Transaction Details
"""
            for transaction in transactions:
                report += f"- {transaction['date']}: {transaction['name']} ({transaction['customer']}) - ${transaction['total_amount']:,.2f} ({transaction['state']})\n"

            logger.info("Generated financial report from Odoo transactions")
            return report.strip()

        except Exception as e:
            logger.error(f"Error generating report from Odoo: {e}")
            return f"Error generating report: {str(e)}"


def main():
    """Main function to demonstrate Odoo integration usage."""
    try:
        odoo_integration = OdooIntegration()

        # Example: Test the connection to Odoo
        odoo_conn = odoo_integration.connect_to_odoo()

        if odoo_conn:
            print("Successfully connected to Odoo!")

            # Example: Read recent transactions
            transactions = odoo_integration.read_transactions()
            print(f"Found {len(transactions)} recent transactions")
        else:
            print("Failed to connect to Odoo. Please check your configuration.")
    except Exception as e:
        logger.error(f"Error in Odoo integration main: {e}")
        audit_logger.log_external_action("odoo_main_error", "odoo", False, {"error": str(e)})
        raise


if __name__ == "__main__":
    main()
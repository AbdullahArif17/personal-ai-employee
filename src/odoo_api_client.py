'''
Safe, reusable Odoo API client for the Personal AI Employee system.
Provides secure and reliable access to Odoo's JSON-RPC API.
'''

import os
import xmlrpc.client
from datetime import datetime
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger, AuditLogger
    from .config import get_config
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger, AuditLogger
    from config import get_config

logger = setup_logger('odoo_api_client')
audit_logger = AuditLogger('odoo_api_client')
config = get_config()

class OdooApiClient:
    """
    Safe, reusable Odoo API client for secure and reliable access to Odoo's JSON-RPC API.
    """

    def __init__(self):
        """Initialize the Odoo API client."""
        self.url = config.odoo_url
        self.db = config.odoo_db
        self.username = config.odoo_username
        self.password = config.odoo_password

        # Connection attributes
        self.uid = None
        self.common = None
        self.models = None
        self.connected = False

    def connect(self) -> bool:
        """
        Connect to the Odoo instance using credentials from config.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            if not all([self.url, self.db, self.username, self.password]):
                logger.error("Missing required Odoo API credentials")
                return False

            # Connect to Odoo using XML-RPC
            self.common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')

            # Authenticate
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
                self.connected = True

                logger.info(f"Successfully connected to Odoo as user ID: {self.uid}")
                audit_logger.log_external_action("connection_success", "odoo", True, {
                    "user_id": self.uid,
                    "db": self.db,
                    "url": self.url
                })
                return True
            else:
                logger.error("Authentication failed for Odoo")
                return False

        except Exception as e:
            logger.error(f"Error connecting to Odoo: {e}")
            audit_logger.log_external_action("connection_error", "odoo", False, {"error": str(e)})
            return False

    def disconnect(self):
        """Disconnect from the Odoo instance."""
        if self.connected:
            self.uid = None
            self.common = None
            self.models = None
            self.connected = False
            logger.info("Disconnected from Odoo")
            audit_logger.log_external_action("disconnected", "odoo", True)

    def is_connected(self) -> bool:
        """
        Check if the client is currently connected to Odoo.

        Returns:
            True if connected, False otherwise
        """
        return self.connected

    def execute_kw(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """
        Execute an Odoo method with the given parameters.

        Args:
            model: Odoo model name (e.g., 'res.partner', 'account.move')
            method: Method name (e.g., 'search', 'read', 'create', 'write')
            args: Arguments for the method (default: [])
            kwargs: Keyword arguments for the method (default: {})

        Returns:
            Result of the method execution, or None if failed
        """
        if not self.connected:
            logger.error("Cannot execute Odoo method: Not connected")
            return None

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )

            logger.debug(f"Successfully executed {model}.{method}")
            return result

        except Exception as e:
            logger.error(f"Error executing {model}.{method}: {e}")
            audit_logger.log_external_action("method_error", "odoo", False, {
                "model": model,
                "method": method,
                "error": str(e)
            })
            return None

    def search_records(self, model: str, domain: List, offset: int = 0, limit: int = None,
                      order: str = None, context: Dict = None) -> List[int]:
        """
        Search for records in an Odoo model.

        Args:
            model: Odoo model name
            domain: Search domain (list of tuples)
            offset: Offset for pagination (default: 0)
            limit: Limit for pagination (default: None)
            order: Order by clause (default: None)
            context: Context dictionary (default: None)

        Returns:
            List of record IDs, or empty list if failed
        """
        kwargs = {}
        if offset != 0:
            kwargs['offset'] = offset
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        if context:
            kwargs['context'] = context

        return self.execute_kw(model, 'search', [domain], kwargs) or []

    def read_records(self, model: str, ids: List[int], fields: List[str] = None,
                     context: Dict = None) -> List[Dict]:
        """
        Read records from an Odoo model.

        Args:
            model: Odoo model name
            ids: List of record IDs to read
            fields: List of fields to read (default: all fields)
            context: Context dictionary (default: None)

        Returns:
            List of record dictionaries, or empty list if failed
        """
        args = [ids]
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if context:
            kwargs['context'] = context

        return self.execute_kw(model, 'read', args, kwargs) or []

    def create_record(self, model: str, values: Dict, context: Dict = None) -> int:
        """
        Create a new record in an Odoo model.

        Args:
            model: Odoo model name
            values: Dictionary of field values for the new record
            context: Context dictionary (default: None)

        Returns:
            ID of the created record, or None if failed
        """
        args = [values]
        kwargs = {}
        if context:
            kwargs['context'] = context

        return self.execute_kw(model, 'create', args, kwargs)

    def update_record(self, model: str, id: int, values: Dict, context: Dict = None) -> bool:
        """
        Update an existing record in an Odoo model.

        Args:
            model: Odoo model name
            id: ID of the record to update
            values: Dictionary of field values to update
            context: Context dictionary (default: None)

        Returns:
            True if successful, False otherwise
        """
        args = [[id], values]
        kwargs = {}
        if context:
            kwargs['context'] = context

        result = self.execute_kw(model, 'write', args, kwargs)
        return result is not False

    def delete_record(self, model: str, id: int, context: Dict = None) -> bool:
        """
        Delete a record from an Odoo model.

        Args:
            model: Odoo model name
            id: ID of the record to delete
            context: Context dictionary (default: None)

        Returns:
            True if successful, False otherwise
        """
        args = [[id]]
        kwargs = {}
        if context:
            kwargs['context'] = context

        result = self.execute_kw(model, 'unlink', args, kwargs)
        return result is not False

    def search_read(self, model: str, domain: List = None, fields: List[str] = None,
                   offset: int = 0, limit: int = None, order: str = None,
                   context: Dict = None) -> List[Dict]:
        """
        Search and read records from an Odoo model in a single call.

        Args:
            model: Odoo model name
            domain: Search domain (default: [])
            fields: List of fields to read (default: all fields)
            offset: Offset for pagination (default: 0)
            limit: Limit for pagination (default: None)
            order: Order by clause (default: None)
            context: Context dictionary (default: None)

        Returns:
            List of record dictionaries, or empty list if failed
        """
        if domain is None:
            domain = []

        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if offset != 0:
            kwargs['offset'] = offset
        if limit:
            kwargs['limit'] = limit
        if order:
            kwargs['order'] = order
        if context:
            kwargs['context'] = context

        return self.execute_kw(model, 'search_read', [domain], kwargs) or []

    def get_model_fields(self, model: str, attributes: List[str] = None) -> Dict:
        """
        Get information about fields in an Odoo model.

        Args:
            model: Odoo model name
            attributes: List of attributes to retrieve (default: all basic attributes)

        Returns:
            Dictionary of field information, or empty dict if failed
        """
        kwargs = {}
        if attributes:
            kwargs['attributes'] = attributes

        return self.execute_kw(model, 'fields_get', [], kwargs) or {}

    def call_method(self, model: str, record_id: int, method_name: str,
                    args: List = None, kwargs: Dict = None) -> Any:
        """
        Call a method on a specific record in an Odoo model.

        Args:
            model: Odoo model name
            record_id: ID of the record
            method_name: Name of the method to call
            args: Arguments for the method (default: [])
            kwargs: Keyword arguments for the method (default: {})

        Returns:
            Result of the method call, or None if failed
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        # Use the special 'call' method to call a record method
        return self.execute_kw(model, 'call', [[record_id], method_name, args], kwargs)


# Global instance for easy access
odoo_api_client = OdooApiClient()


def get_odoo_api_client() -> OdooApiClient:
    """Get the global Odoo API client instance."""
    return odoo_api_client


def ensure_odoo_connection(func):
    """
    Decorator to ensure Odoo connection before executing a function.

    Args:
        func: The function to decorate
    """
    def wrapper(*args, **kwargs):
        client = get_odoo_api_client()
        if not client.is_connected():
            if not client.connect():
                logger.error(f"Cannot execute {func.__name__}: Failed to connect to Odoo")
                return None
        return func(*args, **kwargs)
    return wrapper


# Example usage functions that demonstrate the API client
@ensure_odoo_connection
def create_customer(name: str, email: str = None, phone: str = None) -> Optional[int]:
    """
    Create a new customer (res.partner) in Odoo.

    Args:
        name: Customer name
        email: Customer email (optional)
        phone: Customer phone (optional)

    Returns:
        ID of the created customer, or None if failed
    """
    client = get_odoo_api_client()

    values = {
        'name': name,
        'customer_rank': 1,  # Mark as customer
    }

    if email:
        values['email'] = email
    if phone:
        values['phone'] = phone

    return client.create_record('res.partner', values)


@ensure_odoo_connection
def search_customers(domain: List = None) -> List[Dict]:
    """
    Search for customers in Odoo.

    Args:
        domain: Search domain (default: search for all customers)

    Returns:
        List of customer records, or empty list if failed
    """
    if domain is None:
        domain = [('customer_rank', '>', 0)]  # Only customers

    client = get_odoo_api_client()
    return client.search_read('res.partner', domain, ['name', 'email', 'phone'])


@ensure_odoo_connection
def create_invoice(customer_id: int, line_items: List[Dict],
                   invoice_date: str = None, reference: str = None) -> Optional[int]:
    """
    Create an invoice (account.move) in Odoo.

    Args:
        customer_id: ID of the customer
        line_items: List of line item dictionaries with 'product_id', 'quantity', 'price_unit'
        invoice_date: Invoice date (default: today)
        reference: Invoice reference

    Returns:
        ID of the created invoice, or None if failed
    """
    if invoice_date is None:
        invoice_date = datetime.now().strftime('%Y-%m-%d')

    client = get_odoo_api_client()

    # Prepare invoice line values
    invoice_lines = []
    for item in line_items:
        invoice_lines.append((0, 0, {
            'product_id': item.get('product_id'),
            'name': item.get('name', 'Service'),
            'quantity': item.get('quantity', 1),
            'price_unit': item.get('price_unit', 0),
        }))

    # Prepare invoice values
    invoice_values = {
        'partner_id': customer_id,
        'move_type': 'out_invoice',
        'invoice_date': invoice_date,
        'invoice_line_ids': invoice_lines,
    }

    if reference:
        invoice_values['ref'] = reference

    # Create the invoice
    invoice_id = client.create_record('account.move', invoice_values)

    if invoice_id:
        # Validate and post the invoice
        client.execute_kw('account.move', 'action_post', [[invoice_id]])

    return invoice_id
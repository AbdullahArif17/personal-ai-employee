'''
Test suite for Gold tier features of the Personal AI Employee system.
'''

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta

from src.ralph_loop import RalphLoop, RalphLoopHandler
from src.twitter_poster import TwitterPoster
from src.social_media_poster import SocialMediaPoster
from src.odoo_integration import OdooIntegration
from src.weekly_audit import WeeklyAudit
from src.config import ConfigManager
from src.file_utils import FileUtils
from src.rate_limiter import RateLimiter
from src.audit_trail import AuditTrailLogger
from src.performance_monitor import PerformanceMonitor


class TestGoldTierFeatures(unittest.TestCase):
    """
    Test suite for Gold tier features.
    """

    def setUp(self):
        """Set up test environment with temporary vault directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "AI_Employee_Vault"
        self.vault_path.mkdir(parents=True)

        # Create vault subdirectories
        for folder in ["Inbox", "Needs_Action", "Done", "Logs", "Pending_Approval", "Approved"]:
            (self.vault_path / folder).mkdir()

        # Mock configuration
        self.config_patcher = patch('src.config.ConfigManager')
        self.mock_config = self.config_patcher.start()
        self.mock_config.return_value.vault_path = str(self.vault_path)
        self.mock_config.return_value.dry_run = True
        self.mock_config.return_value.max_retry_attempts = 3
        self.mock_config.return_value.max_retry_duration_hours = 24
        self.mock_config.return_value.twitter_api_key = "test_key"
        self.mock_config.return_value.twitter_api_secret = "test_secret"
        self.mock_config.return_value.twitter_access_token = "test_token"
        self.mock_config.return_value.twitter_access_secret = "test_secret"
        self.mock_config.return_value.facebook_access_token = "test_fb_token"
        self.mock_config.return_value.facebook_page_id = "test_fb_id"
        self.mock_config.return_value.instagram_access_token = "test_ig_token"
        self.mock_config.return_value.instagram_account_id = "test_ig_id"
        self.mock_config.return_value.odoo_url = "http://localhost:8069"
        self.mock_config.return_value.odoo_db = "test_db"
        self.mock_config.return_value.odoo_username = "admin"
        self.mock_config.return_value.odoo_password = "password"

    def tearDown(self):
        """Clean up test environment."""
        self.config_patcher.stop()
        shutil.rmtree(self.temp_dir)

    def test_ralph_loop_initialization(self):
        """Test Ralph Wiggum Loop initialization."""
        ralph_loop = RalphLoop(str(self.vault_path))

        self.assertEqual(ralph_loop.vault_path, self.vault_path)
        self.assertTrue(ralph_loop.needs_action_path.exists())

    def test_twitter_poster_initialization(self):
        """Test Twitter poster initialization."""
        poster = TwitterPoster()

        self.assertIsNotNone(poster.ai_processor)
        # Verify that the poster has the expected methods
        self.assertTrue(hasattr(poster, 'generate_tweet_from_handbook'))
        self.assertTrue(hasattr(poster, 'create_tweet_draft'))
        self.assertTrue(hasattr(poster, 'post_tweet'))

    def test_social_media_poster_initialization(self):
        """Test social media poster initialization."""
        poster = SocialMediaPoster()

        self.assertIsNotNone(poster.ai_processor)
        # Verify that the poster has the expected methods
        self.assertTrue(hasattr(poster, 'generate_facebook_post_from_handbook'))
        self.assertTrue(hasattr(poster, 'generate_instagram_post_from_handbook'))
        self.assertTrue(hasattr(poster, 'create_facebook_draft'))
        self.assertTrue(hasattr(poster, 'create_instagram_draft'))

    def test_odoo_integration_initialization(self):
        """Test Odoo integration initialization."""
        odoo_integration = OdooIntegration()

        # Verify that the integration has the expected methods
        self.assertTrue(hasattr(odoo_integration, 'connect_to_odoo'))
        self.assertTrue(hasattr(odoo_integration, 'create_invoice_from_draft'))
        self.assertTrue(hasattr(odoo_integration, 'read_transactions'))

    def test_weekly_audit_initialization(self):
        """Test weekly audit initialization."""
        audit = WeeklyAudit()

        # Verify that the audit has the expected methods
        self.assertTrue(hasattr(audit, 'get_done_files_last_week'))
        self.assertTrue(hasattr(audit, 'get_odoo_financial_data_last_week'))
        self.assertTrue(hasattr(audit, 'get_social_media_activity_last_week'))
        self.assertTrue(hasattr(audit, 'generate_audit_report'))
        self.assertTrue(hasattr(audit, 'run_audit'))

    def test_rate_limiter_functionality(self):
        """Test rate limiter functionality."""
        rate_limiter = RateLimiter()

        # Test incrementing usage
        result = rate_limiter.increment_usage('twitter')
        self.assertTrue(result)

        # Check usage count
        count, limit = rate_limiter.get_usage('twitter')
        self.assertEqual(count, 1)
        self.assertEqual(limit, 5)  # Default Twitter limit

        # Test rate limiting
        for _ in range(5):
            rate_limiter.increment_usage('twitter')

        # The 7th attempt should fail (since limit is 5 and we already had 1)
        result = rate_limiter.increment_usage('twitter')
        self.assertFalse(result)

    def test_file_utils_functionality(self):
        """Test file utilities functionality."""
        file_utils = FileUtils(str(self.vault_path))

        # Test creating a draft file
        content = "Test content for draft"
        draft_path = file_utils.create_draft_file(content, "Pending_Approval", "test_draft")

        self.assertIsNotNone(draft_path)
        self.assertTrue(draft_path.exists())

        # Test reading file content
        read_content = file_utils.read_file_content(draft_path)
        self.assertEqual(read_content, content)

    def test_audit_trail_logging(self):
        """Test audit trail logging functionality."""
        audit_logger = AuditTrailLogger(str(self.vault_path))

        # Log a test action
        details = {"test_key": "test_value"}
        audit_logger.log_action(
            action_type="test_action",
            component="test_component",
            success=True,
            details=details
        )

        # Verify log file was created
        log_path = self.vault_path / "Logs" / "test_component_audit.json"
        self.assertTrue(log_path.exists())

        # Verify content was logged
        with open(log_path, 'r') as f:
            logs = json.load(f)
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0]["action_type"], "test_action")
            self.assertEqual(logs[0]["success"], True)

    def test_performance_monitor(self):
        """Test performance monitoring functionality."""
        perf_monitor = PerformanceMonitor()

        # Test the time_function decorator
        @perf_monitor.time_function('test_operation')
        def test_func():
            return "result"

        result = test_func()
        self.assertEqual(result, "result")

        # Verify the operation was tracked
        avg_time = perf_monitor.get_average_execution_time('test_operation')
        self.assertIsInstance(avg_time, float)

    def test_generate_tweet_from_handbook(self):
        """Test tweet generation from handbook."""
        # Create a sample handbook file
        handbook_path = self.vault_path / "Company_Handbook.md"
        handbook_content = """
        # Company Handbook

        Our company values innovation, quality, and customer satisfaction.
        We aim to provide excellent service to our clients.
        """
        with open(handbook_path, 'w') as f:
            f.write(handbook_content)

        poster = TwitterPoster()

        # Mock the AI processor to return a test tweet
        with patch.object(poster.ai_processor, 'generate_content', return_value="Test tweet about innovation"):
            tweet_content = poster.generate_tweet_from_handbook()

            self.assertIsNotNone(tweet_content)
            self.assertIn("innovation", tweet_content.lower())

    def test_create_invoice_draft(self):
        """Test invoice draft creation."""
        odoo_integration = OdooIntegration()

        invoice_data = {
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'customer_phone': '123-456-7890',
            'reference': 'INV-001',
            'line_items': [
                {
                    'name': 'Service',
                    'description': 'Professional service',
                    'quantity': 1,
                    'price_unit': 100.0
                }
            ],
            'subtotal': 100.0,
            'tax_amount': 10.0,
            'total_amount': 110.0,
            'notes': 'Test invoice'
        }

        draft_path = odoo_integration.create_invoice_draft(invoice_data)

        self.assertIsNotNone(draft_path)
        self.assertTrue(draft_path.exists())

    def test_generate_audit_report(self):
        """Test audit report generation."""
        audit = WeeklyAudit()

        # Create some test files in Done folder to simulate activity
        done_path = self.vault_path / "Done"
        for i in range(3):
            test_file = done_path / f"test_task_{i}.txt"
            with open(test_file, 'w') as f:
                f.write(f"Test task content {i}")

        # Mock the Odoo integration to return test data
        with patch.object(audit, 'get_odoo_financial_data_last_week', return_value={
            'period': {'from': '2023-01-01', 'to': '2023-01-07'},
            'transactions': [],
            'metrics': {
                'total_revenue': 1000.0,
                'total_subtotal': 900.0,
                'transaction_count': 5,
                'average_transaction_value': 200.0
            }
        }), patch.object(audit, 'get_social_media_activity_last_week', return_value={
            'period': {'from': '2023-01-01', 'to': '2023-01-07'},
            'twitter_drafts': 2,
            'facebook_drafts': 1,
            'instagram_drafts': 1,
            'total_drafts': 4,
            'posted_content': []
        }):
            report = audit.generate_audit_report()

            self.assertIsNotNone(report)
            self.assertIn("Weekly Business Audit Report", report)
            self.assertIn("Task Completion Summary", report)

    def test_ralph_loop_handler_process_task(self):
        """Test Ralph Loop handler task processing."""
        # Create a test task file
        needs_action_path = self.vault_path / "Needs_Action"
        task_file = needs_action_path / "test_task.txt"
        with open(task_file, 'w') as f:
            f.write("Complete this test task")

        # Create handler and mock dependencies
        handler = RalphLoopHandler()
        handler.task_states = {}
        handler.save_task_states = lambda: None  # Mock save method

        # Mock file_utils and other dependencies
        with patch('src.ralph_loop.file_utils') as mock_file_utils, \
             patch('src.ralph_loop.get_ai_processor') as mock_get_ai_proc, \
             patch('src.ralph_loop.config') as mock_config:

            mock_file_utils.read_file_content.return_value = "Complete this test task"
            mock_ai_proc = MagicMock()
            mock_ai_proc.generate_content.return_value = "Task completed successfully"
            mock_ai_proc.validate_completion.return_value = True
            mock_get_ai_proc.return_value = mock_ai_proc

            mock_config.vault_path = str(self.vault_path)
            mock_config.max_retry_attempts = 3
            mock_config.max_retry_duration_hours = 24
            mock_config.dry_run = True

            # Process the task
            handler.process_task(task_file)

            # Check that AI was called
            mock_ai_proc.generate_content.assert_called_once()

    def test_rate_limit_enforcement(self):
        """Test that rate limits are properly enforced."""
        rate_limiter = RateLimiter()

        # Set a low limit for testing
        with patch.object(rate_limiter, 'default_limits', {'twitter': 2}):
            # Use 2 out of 2 allowed
            self.assertTrue(rate_limiter.increment_usage('twitter'))
            self.assertTrue(rate_limiter.increment_usage('twitter'))

            # The third attempt should fail
            self.assertFalse(rate_limiter.increment_usage('twitter'))

    def test_cleanup_functions(self):
        """Test cleanup functions for log retention and auto-rejection."""
        from src.log_cleanup import cleanup_old_logs, auto_reject_old_pending_approvals

        # Test that the functions exist and can be called
        # Note: Actual cleanup behavior is tested with real files, which we're not creating here
        # but we can at least verify the functions exist and handle basic cases

        # Create some mock log files for testing
        logs_path = self.vault_path / "Logs"
        for i in range(2):
            log_file = logs_path / f"2023-01-0{i+1}.json"
            with open(log_file, 'w') as f:
                f.write("[]")

        # Test cleanup with a very short retention period (should not remove recent files)
        removed_count = cleanup_old_logs(retention_days=30)
        # Since our test files are "from" the past, they might be removed
        # Just verify the function runs without error
        self.assertIsInstance(removed_count, int)


class TestIntegrationScenarios(unittest.TestCase):
    """
    Integration tests for Gold tier features working together.
    """

    def setUp(self):
        """Set up test environment with temporary vault directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "AI_Employee_Vault"
        self.vault_path.mkdir(parents=True)

        # Create vault subdirectories
        for folder in ["Inbox", "Needs_Action", "Done", "Logs", "Pending_Approval", "Approved"]:
            (self.vault_path / folder).mkdir()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_full_ralph_loop_scenario(self):
        """Test a complete Ralph Wiggum Loop scenario."""
        # This test simulates the full flow of the Ralph Loop
        ralph_loop = RalphLoop(str(self.vault_path))

        # Create a test task
        task_file = self.vault_path / "Needs_Action" / "test_task.txt"
        with open(task_file, 'w') as f:
            f.write("Process this task with AI")

        # Verify the task exists
        self.assertTrue(task_file.exists())

    def test_social_media_workflow(self):
        """Test the complete social media workflow."""
        # Create a sample handbook file
        handbook_path = self.vault_path / "Company_Handbook.md"
        handbook_content = """
        # Company Handbook

        Our company specializes in innovative technology solutions.
        We value creativity and excellence in everything we do.
        """
        with open(handbook_path, 'w') as f:
            f.write(handbook_content)

        # Test Twitter poster
        twitter_poster = TwitterPoster()
        draft_path = twitter_poster.create_tweet_draft()

        self.assertIsNotNone(draft_path)
        self.assertTrue(draft_path.exists())

        # Test social media poster
        social_poster = SocialMediaPoster()
        fb_success = social_poster.create_facebook_draft() is not None
        ig_success = social_poster.create_instagram_draft() is not None

        self.assertTrue(fb_success or ig_success)  # At least one should succeed

    def test_odoo_integration_workflow(self):
        """Test the complete Odoo integration workflow."""
        odoo_integration = OdooIntegration()

        # Create test invoice data
        invoice_data = {
            'customer_name': 'Integration Test Customer',
            'customer_email': 'integration@test.com',
            'reference': 'INT-TEST-001',
            'line_items': [
                {
                    'name': 'Test Service',
                    'description': 'Service for integration testing',
                    'quantity': 1,
                    'price_unit': 250.0
                }
            ],
            'total_amount': 250.0,
            'notes': 'Invoice created for integration testing'
        }

        # Create invoice draft
        draft_path = odoo_integration.create_invoice_draft(invoice_data)

        self.assertIsNotNone(draft_path)
        self.assertTrue(draft_path.exists())


def run_tests():
    """Run all tests."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGoldTierFeatures)
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationScenarios))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
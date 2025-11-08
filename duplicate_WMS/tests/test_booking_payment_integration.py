"""
Comprehensive integration tests for epic_3_billing booking and payment logic.

Mocks database boundaries and verifies:
- create_booking flow with DB insert
- add_collection_point insert success and failure
- process_cash_payment success, failure, and missing client cases
- linked booking-payment E2E flow
- edge cases for booking with empty date and adding collection points with failure
"""

import os
import sys
import unittest
from unittest.mock import patch
import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TestBookingAndPaymentIntegration(unittest.TestCase):
    """Integration tests for booking and payment logic."""

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_create_booking_success(self, mock_exec):
        """Should return booking_id on successful insert."""
        mock_exec.return_value = 111
        from epic_3_billing.booking_logic import create_booking  # pylint: disable=import-outside-toplevel, import-error
        booking_id = create_booking(1, 2, '2025-11-10')
        self.assertEqual(booking_id, 111)

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_create_booking_empty_date(self, mock_exec):
        """Booking creation with empty date should pass param."""
        mock_exec.return_value = 555
        from epic_3_billing.booking_logic import create_booking  # pylint: disable=import-outside-toplevel, import-error
        booking_id = create_booking(10, 20, '')
        self.assertEqual(booking_id, 555)
        params = mock_exec.call_args[0][1]
        self.assertEqual(params[2], '')

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_add_collection_point_success(self, mock_exec):
        """Returns True on DB insert success."""
        mock_exec.return_value = 10
        from epic_3_billing.booking_logic import add_collection_point  # pylint: disable=import-outside-toplevel, import-error
        ok = add_collection_point(1, 'Home', 'Address 123', 12.3, 45.6)
        self.assertTrue(ok)

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_add_collection_point_fail_none(self, mock_exec):
        """Returns False on DB insert failure."""
        mock_exec.return_value = None
        from epic_3_billing.booking_logic import add_collection_point  # pylint: disable=import-outside-toplevel, import-error
        ok = add_collection_point(1, 'Home', 'Address 123', 12.3, 45.6)
        self.assertFalse(ok)

    @patch('epic_3_billing.payment_logic.fetch_one')
    def test_process_cash_payment_client_not_found(self, mock_fetch_one):
        """Returns False if client lookup fails."""
        mock_fetch_one.return_value = None
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        result = process_cash_payment(9999, 100.0)
        self.assertFalse(result)

    @patch('epic_3_billing.payment_logic.fetch_one')
    @patch('epic_3_billing.payment_logic.execute_query')
    def test_process_cash_payment_success(self, mock_exec, mock_fetch_one):
        """Logs payment and receipt successfully."""
        mock_fetch_one.return_value = {'client_id': 20}
        mock_exec.side_effect = [101, True]
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        ok = process_cash_payment(5, 55.55)
        self.assertTrue(ok)

        receipt_call = mock_exec.call_args_list[1]
        receipt_num = receipt_call[0][1][1]
        current_year = str(datetime.date.today().year)
        self.assertIn(f"RCPT-{current_year}", receipt_num)

    @patch('epic_3_billing.payment_logic.fetch_one')
    @patch('epic_3_billing.payment_logic.execute_query')
    def test_process_cash_payment_insert_fail(self, mock_exec, mock_fetch_one):
        """Returns False if payment insert fails."""
        mock_fetch_one.return_value = {'client_id': 5}
        mock_exec.side_effect = [None]
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        ok = process_cash_payment(15, 20.0)
        self.assertFalse(ok)

    @patch('epic_3_billing.booking_logic.execute_query')
    @patch('epic_3_billing.payment_logic.fetch_one')
    @patch('epic_3_billing.payment_logic.execute_query')
    def test_create_booking_and_process_payment(self, mock_pay_exec, mock_fetch_one, mock_booking_exec):
        """Integration: booking created followed by successful payment."""
        mock_booking_exec.return_value = 777
        mock_fetch_one.return_value = {'client_id': 42}
        mock_pay_exec.side_effect = [9999, True]

        from epic_3_billing.booking_logic import create_booking  # pylint: disable=import-outside-toplevel, import-error
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error

        booking_id = create_booking(10, 5, '2025-11-08')
        self.assertEqual(booking_id, 777)

        ok = process_cash_payment(booking_id, 19.95)
        self.assertTrue(ok)

if __name__ == '__main__':
    unittest.main()

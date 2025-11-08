"""
Unit tests for epic_3_billing.payment_logic.
Mocks DB calls to check cash payment logic edge cases.
"""

import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TestPaymentLogicUnit(unittest.TestCase):
    """Isolated tests for process_cash_payment."""

    @patch('epic_3_billing.payment_logic.execute_query')
    @patch('epic_3_billing.payment_logic.fetch_one')
    def test_process_cash_payment_success(self, mock_fetch_one, mock_exec):
        """Happy path: logs payment, adds receipt, returns True."""
        mock_fetch_one.return_value = {'client_id': 22}
        mock_exec.side_effect = [1001, True]
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        ok = process_cash_payment(15, 33.0)
        self.assertTrue(ok)
        # Check correct SQL for insert
        self.assertIn('INSERT INTO Payments', mock_exec.call_args_list[0][0][0])
        self.assertIn('INSERT INTO Receipts', mock_exec.call_args_list[1][0][0])

    @patch('epic_3_billing.payment_logic.execute_query')
    @patch('epic_3_billing.payment_logic.fetch_one')
    def test_process_cash_payment_payment_id_fail(self, mock_fetch_one, mock_exec):
        """Returns False if payment insert fails."""
        mock_fetch_one.return_value = {'client_id': 10}
        mock_exec.side_effect = [None]
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        ok = process_cash_payment(5, 20.0)
        self.assertFalse(ok)

    @patch('epic_3_billing.payment_logic.execute_query')
    @patch('epic_3_billing.payment_logic.fetch_one')
    def test_process_cash_payment_missing_client(self, mock_fetch_one, mock_exec):
        """Returns False if booking_id is not found."""
        mock_fetch_one.return_value = None
        from epic_3_billing.payment_logic import process_cash_payment  # pylint: disable=import-outside-toplevel, import-error
        ok = process_cash_payment(123, 2.0)
        self.assertFalse(ok)

if __name__ == '__main__':
    unittest.main()

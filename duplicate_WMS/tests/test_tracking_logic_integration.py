"""
Integration tests for epic_2_operations.tracking_logic.mark_stop_complete and related flows.
Mocks DB, geo, payment, but wires together stop updating, payment, and completion check.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Set sys.path for runtime dynamic import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestTrackingLogicIntegration(unittest.TestCase):
    """
    Integration tests for mark_stop_complete and flow combinations.
    """

    @patch('epic_2_operations.tracking_logic._check_and_complete_assignment')
    @patch('epic_2_operations.tracking_logic.execute_query')
    @patch('epic_2_operations.tracking_logic.process_cash_payment')
    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.calculate_distance')
    def test_mark_stop_complete_success_flow(
        self, mock_dist, mock_fetch, mock_pay, mock_exec, mock_check
    ):
        """
        Happy path: mark stop complete, process payment, update DB, call check-complete.
        """
        mock_fetch.side_effect = [
            {'latitude': 12.0, 'longitude': 77.0, 'booking_id': 101, 'assignment_id': 505},
            {'vehicle_id': 66}
        ]
        mock_dist.return_value = 10.0
        mock_pay.return_value = True

        from epic_2_operations.tracking_logic import mark_stop_complete  # pylint: disable=import-outside-toplevel, import-error

        msg = mark_stop_complete(
            driver_id=9, route_stop_id=21, driver_lat=12.0,
            driver_lon=77.0, weight=5.0
        )
        self.assertIn('complete', msg.lower())
        self.assertTrue(mock_pay.called)
        self.assertTrue(mock_exec.called)
        self.assertTrue(mock_check.called)

    @patch('epic_2_operations.tracking_logic.fetch_one')
    def test_mark_stop_complete_no_stop(self, mock_fetch):
        """Returns error if stop not found."""
        mock_fetch.return_value = None
        from epic_2_operations.tracking_logic import mark_stop_complete  # pylint: disable=import-outside-toplevel, import-error
        result = mark_stop_complete(1, 2, 0, 0, 1)
        self.assertIn('not found', result.lower())

    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.calculate_distance')
    def test_mark_stop_complete_too_far(self, mock_dist, mock_fetch):
        """Returns error if driver is too far from stop."""
        mock_fetch.side_effect = [
            {'latitude': 0, 'longitude': 0, 'booking_id': 11, 'assignment_id': 99},
        ]
        mock_dist.return_value = 9000000
        from epic_2_operations.tracking_logic import mark_stop_complete  # pylint: disable=import-outside-toplevel, import-error
        result = mark_stop_complete(1, 2, 10, 10, 3)
        self.assertIn('verification failed', result.lower())

    @patch('epic_2_operations.tracking_logic.process_cash_payment')
    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.calculate_distance')
    def test_mark_stop_complete_payment_fail(self, mock_dist, mock_fetch, mock_pay):
        """Returns error if cash payment fails."""
        mock_fetch.side_effect = [
            {'latitude': 12.0, 'longitude': 77.0, 'booking_id': 202, 'assignment_id': 333},
            None
        ]
        mock_dist.return_value = 5.0
        mock_pay.return_value = False
        from epic_2_operations.tracking_logic import mark_stop_complete  # pylint: disable=import-outside-toplevel, import-error
        out = mark_stop_complete(8, 12, 12.1, 77.1, 3.3)
        self.assertIn('could not process cash payment', out.lower())

    @patch('epic_2_operations.tracking_logic._check_and_complete_assignment')
    @patch('epic_2_operations.tracking_logic.execute_query')
    @patch('epic_2_operations.tracking_logic.process_cash_payment')
    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.calculate_distance')
    def test_mark_stop_complete_no_booking_id(
        self, mock_dist, mock_fetch, mock_pay, mock_exec, mock_check  # pylint: disable=unused-argument
    ):
        """
        Should still try to complete stop even if booking_id is missing (no payment).
        """
        mock_fetch.side_effect = [
            {'latitude': 1.0, 'longitude': 2.0, 'booking_id': None, 'assignment_id': 7},
            None
        ]
        mock_dist.return_value = 1.0
        from epic_2_operations.tracking_logic import mark_stop_complete  # pylint: disable=import-outside-toplevel, import-error
        msg = mark_stop_complete(5, 10, 1.0, 2.0, 7.0)
        self.assertIn('complete', msg.lower())
        mock_pay.assert_not_called()


if __name__ == '__main__':
    unittest.main()

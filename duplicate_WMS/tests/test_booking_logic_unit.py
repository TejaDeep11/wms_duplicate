"""
Unit tests for epic_3_billing.booking_logic functions.
Each test mocks DB side effects and verifies correct parameters and return shape.
"""

import os
import sys
import unittest
from unittest.mock import patch

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestBookingLogicUnit(unittest.TestCase):
    """Isolated unit tests for booking logic."""

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_create_booking_success(self, mock_exec):
        """create_booking returns booking_id from DB."""
        mock_exec.return_value = 111
        from epic_3_billing.booking_logic import create_booking  # pylint: disable=import-outside-toplevel, import-error
        result = create_booking(1, 2, '2025-01-01')
        self.assertEqual(result, 111)
        sql, params = mock_exec.call_args[0]
        self.assertIn('INSERT INTO ServiceBookings', sql)
        self.assertEqual(params, (1, 2, '2025-01-01'))

    @patch('epic_3_billing.booking_logic.fetch_all')
    def test_get_client_bookings(self, mock_fetch):
        """get_client_bookings returns aggregates from join query."""
        mock_fetch.return_value = [{'requested_date': '2025-01-01', 'point_name': 'Home', 'job_status': 'Done'}]
        from epic_3_billing.booking_logic import get_client_bookings  # pylint: disable=import-outside-toplevel, import-error
        result = get_client_bookings(5)
        self.assertTrue(result[0].get('point_name'))
        sql, params = mock_fetch.call_args[0]
        self.assertIn('FROM ServiceBookings', sql)
        self.assertEqual(params, (5,))

    @patch('epic_3_billing.booking_logic.fetch_all')
    def test_get_client_collection_points(self, mock_fetch):
        """get_client_collection_points returns point IDs for client."""
        mock_fetch.return_value = [{'point_id': 2, 'point_name': 'Office'}]
        from epic_3_billing.booking_logic import get_client_collection_points  # pylint: disable=import-outside-toplevel, import-error
        points = get_client_collection_points(8)
        self.assertTrue(points)
        sql, params = mock_fetch.call_args[0]
        self.assertIn('FROM CollectionPoints', sql)
        self.assertEqual(params, (8,))

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_add_collection_point_success(self, mock_exec):
        """add_collection_point returns True on valid DB insert."""
        mock_exec.return_value = 10
        from epic_3_billing.booking_logic import add_collection_point  # pylint: disable=import-outside-toplevel, import-error
        ok = add_collection_point(1, 'Home', '123 St', 1.0, 2.0)
        self.assertTrue(ok)
        sql, params = mock_exec.call_args[0]
        self.assertIn('INSERT INTO CollectionPoints', sql)
        self.assertEqual(params, (1, 'Home', '123 St', 1.0, 2.0))

    @patch('epic_3_billing.booking_logic.execute_query')
    def test_add_collection_point_fail(self, mock_exec):
        """add_collection_point returns False if DB insert fails."""
        mock_exec.return_value = None
        from epic_3_billing.booking_logic import add_collection_point  # pylint: disable=import-outside-toplevel, import-error
        ok = add_collection_point(1, 'Home', '123 St', 1.0, 2.0)
        self.assertFalse(ok)


if __name__ == '__main__':
    unittest.main()

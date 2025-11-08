"""
Unit tests for epic_1_routing.assignment_logic individual helpers:
- get_available_drivers
- get_available_vehicles
- get_pending_bookings
- get_daily_booking_report
- get_active_vehicles_by_date

DB calls are mocked to verify query wiring and return shapes.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is available for runtime imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestAssignmentListQueries(unittest.TestCase):
    """Tests for list-retrieval functions with mocked DB boundaries."""

    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_get_available_drivers(self, mock_fetch_all):
        """Should call fetch_all with expected SQL and return data as-is."""
        mock_fetch_all.return_value = [{'user_id': 1, 'first_name': 'D', 'last_name': 'R'}]
        from epic_1_routing.assignment_logic import get_available_drivers  # pylint: disable=import-outside-toplevel, import-error

        result = get_available_drivers()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['user_id'], 1)
        sql = mock_fetch_all.call_args[0][0]
        self.assertIn('FROM Users', sql)

    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_get_available_vehicles(self, mock_fetch_all):
        """Should call fetch_all with expected SQL and return data as-is."""
        mock_fetch_all.return_value = [{'vehicle_id': 10, 'license_plate': 'KA01', 'model': 'T'}]
        from epic_1_routing.assignment_logic import get_available_vehicles  # pylint: disable=import-outside-toplevel, import-error

        result = get_available_vehicles()
        self.assertEqual(result[0]['vehicle_id'], 10)
        sql = mock_fetch_all.call_args[0][0]
        self.assertIn('FROM Vehicles', sql)

    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_get_pending_bookings(self, mock_fetch_all):
        """Should return bookings not yet assigned today."""
        mock_fetch_all.return_value = [{'booking_id': 99, 'point_id': 3, 'latitude': 1.23, 'longitude': 4.56}]
        from epic_1_routing.assignment_logic import get_pending_bookings  # pylint: disable=import-outside-toplevel, import-error

        result = get_pending_bookings()
        self.assertEqual(result[0]['booking_id'], 99)
        sql = mock_fetch_all.call_args[0][0]
        self.assertIn('FROM ServiceBookings', sql)

    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_get_daily_booking_report(self, mock_fetch_all):
        """Should return report rows for today."""
        mock_fetch_all.return_value = [{'first_name': 'A', 'job_status': 'Approved', 'payment_status': 'Paid', 'amount_paid': 100}]
        from epic_1_routing.assignment_logic import get_daily_booking_report  # pylint: disable=import-outside-toplevel, import-error

        result = get_daily_booking_report()
        self.assertEqual(result[0]['payment_status'], 'Paid')
        sql = mock_fetch_all.call_args[0][0]
        self.assertIn('FROM ServiceBookings', sql)
        self.assertIn('LEFT JOIN Payments', sql)

    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_get_active_vehicles_by_date(self, mock_fetch_all):
        """Should pass date param and return active vehicles for that date."""
        mock_fetch_all.return_value = [{'vehicle_id': 7, 'license_plate': 'KA02', 'model': 'X'}]
        from epic_1_routing.assignment_logic import get_active_vehicles_by_date  # pylint: disable=import-outside-toplevel, import-error

        result = get_active_vehicles_by_date('2025-01-01')
        self.assertEqual(result[0]['vehicle_id'], 7)
        args = mock_fetch_all.call_args[0]
        self.assertIn('%s', args[0])  # SQL contains placeholder
        self.assertEqual(args[1], ('2025-01-01',))


if __name__ == '__main__':
    unittest.main()

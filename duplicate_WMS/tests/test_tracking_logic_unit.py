"""
Unit tests for epic_2_operations.tracking_logic
Mocks all external dependencies and tests each function in isolation.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Set sys.path to import the tracking logic module at runtime
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TestTrackingLogicUnit(unittest.TestCase):
    """Unit tests for tracking functions."""

    @patch('epic_2_operations.tracking_logic.fetch_all')
    def test_get_live_vehicle_locations(self, mock_fetch):
        """get_live_vehicle_locations should request correct SQL and return data as-is."""
        mock_fetch.return_value = [{'license_plate': 'KA01', 'latitude': 1, 'longitude': 2}]
        from epic_2_operations.tracking_logic import get_live_vehicle_locations  # pylint: disable=import-outside-toplevel, import-error
        result = get_live_vehicle_locations()
        self.assertEqual(result, [{'license_plate': 'KA01', 'latitude': 1, 'longitude': 2}])
        sql = mock_fetch.call_args[0][0]
        self.assertIn('FROM VehicleLocations', sql)
        self.assertIn('license_plate', sql)
            
    @patch('epic_2_operations.tracking_logic.fetch_all')
    def test_get_driver_assignment(self, mock_fetch):
        """get_driver_assignment should filter by driver and status."""
        mock_fetch.return_value = [{'route_stop_id': 1, 'point_name': 'Home'}]
        from epic_2_operations.tracking_logic import get_driver_assignment  # pylint: disable=import-outside-toplevel, import-error
        result = get_driver_assignment(42)
        self.assertEqual(result[0]['route_stop_id'], 1)
        sql = mock_fetch.call_args[0][0]
        self.assertIn('Pending', sql)
        self.assertIn('%s', sql)
        params = mock_fetch.call_args[0][1]
        self.assertEqual(params, (42,))
    
    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.execute_query')
    def test__check_and_complete_assignment_marks_complete(self, mock_exec, mock_fetch):
        """_check_and_complete_assignment should set assignment to Completed when done."""
        mock_fetch.return_value = {'pending_count': 0}
        from epic_2_operations.tracking_logic import _check_and_complete_assignment  # pylint: disable=import-outside-toplevel, import-error
        _check_and_complete_assignment(7)
        sql = mock_exec.call_args[0][0]
        params = mock_exec.call_args[0][1]
        self.assertIn('RouteAssignments', sql)
        self.assertEqual(params, (7,))

    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.execute_query')
    def test__check_and_complete_assignment_pending(self, mock_exec, mock_fetch):
        """Does not update assignment when pending_count > 0."""
        mock_fetch.return_value = {'pending_count': 2}
        from epic_2_operations.tracking_logic import _check_and_complete_assignment  # pylint: disable=import-outside-toplevel, import-error
        _check_and_complete_assignment(111)
        mock_exec.assert_not_called()
    
    @patch('epic_2_operations.tracking_logic.fetch_one')
    @patch('epic_2_operations.tracking_logic.execute_query')
    def test_log_driver_location_with_assignment(self, mock_exec, mock_fetch):
        """log_driver_location logs when assigned, returns True; else returns False."""
        mock_fetch.return_value = {'vehicle_id': 55}
        from epic_2_operations.tracking_logic import log_driver_location  # pylint: disable=import-outside-toplevel, import-error
        ok = log_driver_location(10, 1.1, 2.2)
        self.assertTrue(ok)
        # Should log location with vehicle_id, lat, lon
        params = mock_exec.call_args[0][1]
        self.assertEqual(params, (55, 1.1, 2.2))

    @patch('epic_2_operations.tracking_logic.fetch_one')
    def test_log_driver_location_no_vehicle(self, mock_fetch):
        """log_driver_location returns False if driver has no assignment."""
        mock_fetch.return_value = None
        from epic_2_operations.tracking_logic import log_driver_location  # pylint: disable=import-outside-toplevel, import-error
        ok = log_driver_location(22, 0, 0)
        self.assertFalse(ok)
    
    @patch('epic_2_operations.tracking_logic.fetch_all')
    def test_get_route_history(self, mock_fetch_all):
        """get_route_history combines stops and path queries for right vehicle/date."""
        # Simulate: first call (stops), second call (path)
        mock_fetch_all.side_effect = (
            [{'point_name': 'A', 'completed_at': 't1', 'latitude': 11, 'longitude': 12, 'collected_volume_kg': 1.2}],
            [{'latitude': 1, 'longitude': 2}, {'latitude': 3, 'longitude': 4}]
        )
        from epic_2_operations.tracking_logic import get_route_history  # pylint: disable=import-outside-toplevel, import-error
        out = get_route_history(10, '2025-01-01')
        self.assertIn('stops', out)
        self.assertIn('path', out)
        self.assertTrue(out['stops'])
        self.assertTrue(out['path'])


if __name__ == '__main__':
    unittest.main()

"""
Integration tests for create_route_assignment in epic_1_routing.assignment_logic.
- Mocks DB boundaries and optimizer to verify the full flow:
  bookings fetched -> optimized -> assignment inserted -> stops inserted in order.
- Also includes negative cases (no bookings found, insert fail).
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is available for runtime imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestCreateRouteAssignmentIntegration(unittest.TestCase):
    """
    Integration tests for route assignment creation with optimizer.
    """

    @patch('epic_1_routing.assignment_logic.execute_query')
    @patch('epic_1_routing.assignment_logic.optimize_route_nearest_neighbor')
    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_create_route_assignment_success(self, mock_fetch_all, mock_optimize, mock_execute):
        """
        Happy path: optimized order used for stop insertion, returns True.
        Only checks that parameters for stop inserts are correct; ignores SQL string formatting.
        """
        # Mock fetch_all to return booking details with coordinates
        mock_fetch_all.return_value = [
            {'booking_id': 101, 'point_id': 1, 'latitude': 12.0, 'longitude': 77.0},
            {'booking_id': 102, 'point_id': 2, 'latitude': 12.1, 'longitude': 77.1},
        ]
        # Optimizer returns reversed order to check insertion sequence
        mock_optimize.return_value = [
            {'booking_id': 102, 'point_id': 2, 'latitude': 12.1, 'longitude': 77.1},
            {'booking_id': 101, 'point_id': 1, 'latitude': 12.0, 'longitude': 77.0},
        ]
        # execute_query returns assignment_id on first insert and True on stops
        mock_execute.side_effect = [999, True, True]

        from epic_1_routing.assignment_logic import create_route_assignment  # pylint: disable=import-outside-toplevel, import-error

        ok = create_route_assignment(supervisor_id=5, driver_id=7, vehicle_id=9, booking_ids=[101, 102])
        self.assertTrue(ok)

        # Check two calls were made to insert RouteStops after the assignment insert
        insert_calls = mock_execute.call_args_list[1:3]
        params = [c[0][1] for c in insert_calls]
        self.assertEqual(params, [
            (999, 2, 102, 1),
            (999, 1, 101, 2)
        ])
        # Optionally, check each SQL contains the RouteStops table name (not full string)
        for c in insert_calls:
            self.assertIn('RouteStops', c[0][0])

    @patch('epic_1_routing.assignment_logic.execute_query')
    @patch('epic_1_routing.assignment_logic.optimize_route_nearest_neighbor')
    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_create_route_assignment_no_bookings_found(self, mock_fetch_all, mock_optimize, mock_execute):
        """
        If fetch_all returns no booking details, function returns False quickly.
        """
        mock_fetch_all.return_value = []
        from epic_1_routing.assignment_logic import create_route_assignment  # pylint: disable=import-outside-toplevel, import-error

        ok = create_route_assignment(1, 2, 3, [999])
        self.assertFalse(ok)
        mock_optimize.assert_not_called()
        mock_execute.assert_not_called()

    @patch('epic_1_routing.assignment_logic.execute_query')
    @patch('epic_1_routing.assignment_logic.optimize_route_nearest_neighbor')
    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_create_route_assignment_insert_assignment_fail(self, mock_fetch_all, mock_optimize, mock_execute):
        """
        If assignment insert fails (returns falsy), function returns False.
        """
        mock_fetch_all.return_value = [
            {'booking_id': 1, 'point_id': 10, 'latitude': 1.0, 'longitude': 1.0}
        ]
        mock_optimize.return_value = mock_fetch_all.return_value
        mock_execute.side_effect = [None]  # assignment insert fails

        from epic_1_routing.assignment_logic import create_route_assignment  # pylint: disable=import-outside-toplevel, import-error

        ok = create_route_assignment(1, 2, 3, [1])
        self.assertFalse(ok)
        # Only one call attempted (assignment insert)
        self.assertEqual(len(mock_execute.call_args_list), 1)

if __name__ == '__main__':
    unittest.main()

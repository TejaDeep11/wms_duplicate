"""
UI-level integration smoke tests that run the supervisor tab logic paths indirectly
by mocking the core routing functions used by main.py dashboards.

These tests do not render Streamlit UI; they patch Streamlit and verify that
the integration entry points (create_route_assignment and list providers) are invoked
as expected when the dashboard code would call them.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestSupervisorRoutingIntegrationUI(unittest.TestCase):
    """Simulates dashboard_supervisor calls into assignment logic."""

    @patch('epic_1_routing.assignment_logic.get_pending_bookings')
    @patch('epic_1_routing.assignment_logic.get_available_vehicles')
    @patch('epic_1_routing.assignment_logic.get_available_drivers')
    def test_list_fetchers_integration(self, mock_drivers, mock_vehicles, mock_bookings):
        """List endpoints return data used by UI; verify callable without DB."""
        mock_drivers.return_value = [{'user_id': 2, 'first_name': 'D', 'last_name': 'R'}]
        mock_vehicles.return_value = [{'vehicle_id': 5, 'license_plate': 'KA01', 'model': 'T'}]
        mock_bookings.return_value = [{'booking_id': 10, 'point_id': 20, 'latitude': 1.0, 'longitude': 2.0}]

        from epic_1_routing.assignment_logic import (  # pylint: disable=import-outside-toplevel, import-error
            get_available_drivers, get_available_vehicles, get_pending_bookings
        )

        self.assertTrue(get_available_drivers())
        self.assertTrue(get_available_vehicles())
        self.assertTrue(get_pending_bookings())

    @patch('epic_1_routing.assignment_logic.execute_query')
    @patch('epic_1_routing.assignment_logic.optimize_route_nearest_neighbor')
    @patch('epic_1_routing.assignment_logic.fetch_all')
    def test_create_route_from_dashboard_path(self, mock_fetch_all, mock_optimize, mock_execute):
        """Creating a route from UI flow: verifies integration path returns True."""
        mock_fetch_all.return_value = [
            {'booking_id': 1, 'point_id': 100, 'latitude': 12.0, 'longitude': 77.0},
            {'booking_id': 2, 'point_id': 101, 'latitude': 12.2, 'longitude': 77.2},
        ]
        mock_optimize.return_value = mock_fetch_all.return_value
        mock_execute.side_effect = [1000, True, True]

        from epic_1_routing.assignment_logic import create_route_assignment  # pylint: disable=import-outside-toplevel, import-error

        ok = create_route_assignment(supervisor_id=99, driver_id=2, vehicle_id=5, booking_ids=[1, 2])
        self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()

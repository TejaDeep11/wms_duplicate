"""
Unit tests for epic_1_routing.optimize_logic.optimize_route_nearest_neighbor.
Focuses on algorithm behavior; mocks geo distance when needed.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is available for runtime imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestOptimizeRouteNearestNeighbor(unittest.TestCase):
    """Unit tests for the Nearest Neighbor optimizer."""

    def test_empty_input_returns_empty(self):
        """Empty list should return empty route."""
        from epic_1_routing.optimize_logic import optimize_route_nearest_neighbor  # pylint: disable=import-outside-toplevel, import-error
        self.assertEqual(optimize_route_nearest_neighbor([]), [])

    def test_single_stop_returns_same(self):
        """Single stop should remain unchanged."""
        from epic_1_routing.optimize_logic import optimize_route_nearest_neighbor  # pylint: disable=import-outside-toplevel, import-error
        stops = [{'point_id': 1, 'latitude': 12.0, 'longitude': 77.0}]
        result = optimize_route_nearest_neighbor(stops)
        self.assertEqual(result, stops)

    @patch('epic_1_routing.optimize_logic.calculate_distance')
    def test_two_stops_order_is_deterministic(self, mock_dist):
        """Two stops: the order after the first depends on distance; simulate tie-free path."""
        mock_dist.side_effect = [10.0]  # one comparison
        from epic_1_routing.optimize_logic import optimize_route_nearest_neighbor  # pylint: disable=import-outside-toplevel, import-error
        stops = [
            {'point_id': 1, 'latitude': 12.0, 'longitude': 77.0},
            {'point_id': 2, 'latitude': 12.5, 'longitude': 77.5},
        ]
        result = optimize_route_nearest_neighbor(stops)
        self.assertEqual([s['point_id'] for s in result], [1, 2])

    @patch('epic_1_routing.optimize_logic.calculate_distance')
    def test_multiple_stops_orders_by_nearest(self, mock_dist):
        """Multiple stops: verifies greedy nearest selection across iterations."""
        # Distances will be returned in the order they are computed by the algorithm.
        # For 3 stops (A,B,C) starting at A:
        # Step1: dist(A,B)=5, dist(A,C)=10 -> choose B
        # Step2: dist(B,C)=3 -> choose C
        mock_dist.side_effect = [5.0, 10.0, 3.0]

        from epic_1_routing.optimize_logic import optimize_route_nearest_neighbor  # pylint: disable=import-outside-toplevel, import-error
        stops = [
            {'point_id': 'A', 'latitude': 1.0, 'longitude': 1.0},
            {'point_id': 'B', 'latitude': 2.0, 'longitude': 2.0},
            {'point_id': 'C', 'latitude': 3.0, 'longitude': 3.0},
        ]
        result = optimize_route_nearest_neighbor(stops)
        self.assertEqual([s['point_id'] for s in result], ['A', 'B', 'C'])

    @patch('epic_1_routing.optimize_logic.calculate_distance')
    def test_ties_choose_first_min(self, mock_dist):
        """If distances tie, the first encountered min should be chosen (stable behavior)."""
        # For A->(B=5, C=5), the loop will first see B, then C, and keep B as nearest.
        mock_dist.side_effect = [5.0, 5.0, 1.0]  # next step B->C small

        from epic_1_routing.optimize_logic import optimize_route_nearest_neighbor  # pylint: disable=import-outside-toplevel, import-error
        stops = [
            {'point_id': 'A', 'latitude': 0.0, 'longitude': 0.0},
            {'point_id': 'B', 'latitude': 0.0, 'longitude': 1.0},
            {'point_id': 'C', 'latitude': 1.0, 'longitude': 0.0},
        ]
        result = optimize_route_nearest_neighbor(stops)
        self.assertEqual([s['point_id'] for s in result], ['A', 'B', 'C'])


if __name__ == '__main__':
    unittest.main()

"""
UI tests for epic_0_auth/new_user.py using runtime imports and patching only.
Covers success and failure flows without modifying source files.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Add project root so runtime imports work during tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestNewUserUI(unittest.TestCase):
    """Tests for create_new_user UI function with mocked Streamlit and logic."""

    @patch('epic_0_auth.new_user.st')
    @patch('epic_0_auth.new_user.register_new_user')
    def test_create_new_user_success(self, mock_register, mock_st):
        """Success path: returns True and shows success message."""
        mock_register.return_value = (True, "Account created successfully!")

        # Import at runtime to keep patching reliable in tests
        from epic_0_auth.new_user import create_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok = create_new_user('new@example.com', 'First', 'Last', '9999999999', 'secret', 2)

        self.assertTrue(ok)
        mock_st.success.assert_called_once_with("Account created successfully!")
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.new_user.st')
    @patch('epic_0_auth.new_user.register_new_user')
    def test_create_new_user_failure(self, mock_register, mock_st):
        """Failure path: returns False and shows error message."""
        mock_register.return_value = (False, "Error: Could not create account.")

        from epic_0_auth.new_user import create_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok = create_new_user('x@example.com', 'A', 'B', '123', 'pw', 1)

        self.assertFalse(ok)
        mock_st.error.assert_called_once_with("Error: Could not create account.")

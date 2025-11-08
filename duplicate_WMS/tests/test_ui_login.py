"""
Tests for Streamlit UI login wrapper in epic_0_auth/login.py.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from epic_0_auth import login as login_mod  # noqa: E0401


class TestLoginUI(unittest.TestCase):
    """Tests for the login UI function."""

    @patch('epic_0_auth.login.st')
    @patch('epic_0_auth.login.verify_user_login')
    def test_login_success(self, mock_verify, mock_st):
        """Successful login updates session_state and reruns."""
        mock_verify.return_value = {
            'user_id': 42,
            'first_name': 'Ada',
            'role_name': 'Admin',
            'password_hash': 'x'
        }
        mock_st.session_state = {}
        mock_st.rerun = MagicMock()

        login_mod.login('ada@example.com', 'correct')

        assert mock_st.session_state['logged_in'] is True
        assert mock_st.session_state['user_id'] == 42
        assert mock_st.session_state['role'] == 'Admin'
        assert mock_st.session_state['first_name'] == 'Ada'
        mock_st.rerun.assert_called_once()
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.login.st')
    @patch('epic_0_auth.login.verify_user_login')
    def test_login_incorrect_password(self, mock_verify, mock_st):
        """Incorrect password shows error and does not set session."""
        mock_verify.return_value = "Error: Incorrect password."
        mock_st.session_state = {}

        login_mod.login('user@example.com', 'wrong')

        mock_st.error.assert_called_once()
        assert 'logged_in' not in mock_st.session_state

    @patch('epic_0_auth.login.st')
    def test_login_requires_both_fields(self, mock_st):
        """Missing email/password shows validation error early."""
        mock_st.session_state = {}

        login_mod.login('', '')
        mock_st.error.assert_called_once_with("Please enter both email and password.")

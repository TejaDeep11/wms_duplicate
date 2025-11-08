"""
Tests for Streamlit UI forgot-password wrappers in epic_0_auth/forgot_password.py.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root is on sys.path for pylint/static analysis and runtime
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Top-level imports so pylint can resolve modules
from epic_0_auth import forgot_password  # noqa: E0401


class TestForgotPasswordUI(unittest.TestCase):
    """Tests for request_password_reset and reset_password functions."""

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_otp_request')
    def test_request_password_reset_success(self, mock_logic, mock_st):
        """Success shows success toast."""
        mock_logic.return_value = (True, "OTP sent")

        forgot_password.request_password_reset('user@example.com')
        mock_st.success.assert_called_once_with("OTP sent")
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_otp_request')
    def test_request_password_reset_failure(self, mock_logic, mock_st):
        """Failure shows error toast."""
        mock_logic.return_value = (False, "Error: mail failed")

        forgot_password.request_password_reset('user@example.com')
        mock_st.error.assert_called_once_with("Error: mail failed")

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_password_reset')
    def test_reset_password_success(self, mock_logic, mock_st):
        """Success returns True and shows success."""
        mock_logic.return_value = (True, "OK")

        ok = forgot_password.reset_password('user@example.com', '123456', 'newpass')
        assert ok is True
        mock_st.success.assert_called_once_with("OK")
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_password_reset')
    def test_reset_password_failure(self, mock_logic, mock_st):
        """Failure returns False and shows error."""
        mock_logic.return_value = (False, "Error: bad otp")

        ok = forgot_password.reset_password('user@example.com', '000000', 'newpass')
        assert ok is False
        mock_st.error.assert_called_once_with("Error: bad otp")

"""
Integration tests for epic_0_auth UI wrappers only:
- login.login
- new_user.create_new_user
- forgot_password.request_password_reset, reset_password

Mocks Streamlit and underlying logic calls to validate UI integration behavior.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure project root on sys.path for runtime imports inside tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestEpic0AuthUIIntegration(unittest.TestCase):
    """Integration tests for Streamlit-facing UI wrappers in epic_0_auth."""

    @patch('epic_0_auth.login.st')
    @patch('epic_0_auth.login.verify_user_login')
    def test_login_ui_success(self, mock_verify, mock_st):
        """Login UI: success updates session and reruns."""
        mock_verify.return_value = {
            'user_id': 55,
            'first_name': 'Mira',
            'role_name': 'Client',
            'password_hash': 'x',
        }
        mock_st.session_state = {}
        mock_st.rerun = MagicMock()

        from epic_0_auth.login import login  # pylint: disable=import-outside-toplevel, import-error

        login('mira@example.com', 'pw')

        self.assertTrue(mock_st.session_state['logged_in'])
        self.assertEqual(mock_st.session_state['user_id'], 55)
        self.assertEqual(mock_st.session_state['role'], 'Client')
        self.assertEqual(mock_st.session_state['first_name'], 'Mira')
        mock_st.rerun.assert_called_once()
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.login.st')
    @patch('epic_0_auth.login.verify_user_login')
    def test_login_ui_failure(self, mock_verify, mock_st):
        """Login UI: failure shows error and does not set session."""
        mock_verify.return_value = "Error: Incorrect password."
        mock_st.session_state = {}

        from epic_0_auth.login import login  # pylint: disable=import-outside-toplevel, import-error

        login('u@example.com', 'wrong')
        mock_st.error.assert_called_once()
        self.assertNotIn('logged_in', mock_st.session_state)

    @patch('epic_0_auth.new_user.st')
    @patch('epic_0_auth.new_user.register_new_user')
    def test_new_user_ui_success(self, mock_register, mock_st):
        """New user UI: success returns True and shows success message."""
        mock_register.return_value = (True, "Account created successfully!")
        mock_st.rerun = MagicMock()

        from epic_0_auth.new_user import create_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok = create_new_user('a@b.com', 'A', 'B', '999', 'pw', 2)
        self.assertTrue(ok)
        mock_st.success.assert_called_once()
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.new_user.st')
    @patch('epic_0_auth.new_user.register_new_user')
    def test_new_user_ui_failure(self, mock_register, mock_st):
        """New user UI: failure returns False and shows error message."""
        mock_register.return_value = (False, "Error: Could not create account.")

        from epic_0_auth.new_user import create_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok = create_new_user('a@b.com', 'A', 'B', '999', 'pw', 2)
        self.assertFalse(ok)
        mock_st.error.assert_called_once()

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_otp_request')
    def test_forgot_ui_request_success(self, mock_logic, mock_st):
        """Forgot-password UI: request success shows success message."""
        mock_logic.return_value = (True, "OTP sent")

        from epic_0_auth.forgot_password import request_password_reset  # pylint: disable=import-outside-toplevel, import-error

        request_password_reset('u@example.com')
        mock_st.success.assert_called_once_with("OTP sent")
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_otp_request')
    def test_forgot_ui_request_failure(self, mock_logic, mock_st):
        """Forgot-password UI: request failure shows error message."""
        mock_logic.return_value = (False, "Error: mail failed")

        from epic_0_auth.forgot_password import request_password_reset  # pylint: disable=import-outside-toplevel, import-error

        request_password_reset('u@example.com')
        mock_st.error.assert_called_once_with("Error: mail failed")

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_password_reset')
    def test_forgot_ui_reset_success(self, mock_logic, mock_st):
        """Forgot-password UI: reset success returns True and shows success."""
        mock_logic.return_value = (True, "OK")

        from epic_0_auth.forgot_password import reset_password  # pylint: disable=import-outside-toplevel, import-error

        ok = reset_password('u@example.com', '123456', 'newpw')
        self.assertTrue(ok)
        mock_st.success.assert_called_once_with("OK")
        mock_st.error.assert_not_called()

    @patch('epic_0_auth.forgot_password.st')
    @patch('epic_0_auth.forgot_password.handle_password_reset')
    def test_forgot_ui_reset_failure(self, mock_logic, mock_st):
        """Forgot-password UI: reset failure returns False and shows error."""
        mock_logic.return_value = (False, "Error: bad otp")

        from epic_0_auth.forgot_password import reset_password  # pylint: disable=import-outside-toplevel, import-error

        ok = reset_password('u@example.com', '000000', 'newpw')
        self.assertFalse(ok)
        mock_st.error.assert_called_once_with("Error: bad otp")


if __name__ == '__main__':
    unittest.main()

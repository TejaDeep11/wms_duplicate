"""
Integration tests for epic_0_auth core logic:
- verify_user_login
- register_new_user
- handle_otp_request
- handle_password_reset

Mocks only external boundaries (DB + email) to wire functions together.
"""

import os
import sys
import unittest
from unittest.mock import patch

# Ensure project root on sys.path for runtime imports inside tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestEpic0AuthLogicIntegration(unittest.TestCase):
    """End-to-end style integration tests for epic_0_auth core logic."""

    @patch('epic_0_auth.auth_utils.fetch_one')
    @patch('epic_0_auth.auth_utils.check_password')
    def test_login_success_flow(self, mock_check, mock_fetch):
        """Existing user + correct password returns full user dict."""
        mock_fetch.return_value = {
            'user_id': 11,
            'first_name': 'Jane',
            'password_hash': 'bcrypt$hash',
            'role_name': 'Supervisor',
        }
        mock_check.return_value = True

        # Runtime import for reliable patching in test env
        from epic_0_auth.auth_utils import verify_user_login  # pylint: disable=import-outside-toplevel, import-error

        result = verify_user_login('jane@example.com', 'rightpw')
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 11)
        self.assertEqual(result['role_name'], 'Supervisor')

    @patch('epic_0_auth.auth_utils.fetch_one')
    def test_login_user_not_found(self, mock_fetch):
        """Missing user returns specific error string."""
        mock_fetch.return_value = None

        from epic_0_auth.auth_utils import verify_user_login  # pylint: disable=import-outside-toplevel, import-error

        result = verify_user_login('ghost@example.com', 'pw')
        self.assertEqual(result, "Error: User not found.")

    @patch('epic_0_auth.auth_utils.check_password')
    @patch('epic_0_auth.auth_utils.fetch_one')
    def test_login_wrong_password(self, mock_fetch, mock_check):
        """Wrong password returns error and does not leak details."""
        mock_fetch.return_value = {
            'user_id': 20,
            'first_name': 'Rick',
            'password_hash': 'hash',
            'role_name': 'Driver',
        }
        mock_check.return_value = False

        from epic_0_auth.auth_utils import verify_user_login  # pylint: disable=import-outside-toplevel, import-error

        result = verify_user_login('rick@example.com', 'badpw')
        self.assertEqual(result, "Error: Incorrect password.")

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_success_flow(self, mock_hash, mock_get, mock_exec):
        """Register: no duplicate -> insert -> success message."""
        mock_get.return_value = None
        mock_hash.return_value = 'hashed_pw'
        mock_exec.return_value = 321

        from epic_0_auth.auth_utils import register_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok, msg = register_new_user(
            'new@example.com', 'First', 'Last', '9999999999', 'pw', 2
        )
        self.assertTrue(ok)
        self.assertIn('success', msg.lower())

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_register_duplicate_email(self, mock_get):
        """Register: duplicate email short-circuits with clear error."""
        mock_get.return_value = {'user_id': 1}

        from epic_0_auth.auth_utils import register_new_user  # pylint: disable=import-outside-toplevel, import-error

        ok, msg = register_new_user(
            'dup@example.com', 'A', 'B', '123', 'pw', 3
        )
        self.assertFalse(ok)
        self.assertIn('already exists', msg)

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_request_success_flow(self, mock_get, mock_send):
        """OTP request: user exists, email sent, OTP stored with 6 digits."""
        mock_get.return_value = {'user_id': 77, 'email': 'u@example.com'}
        mock_send.return_value = True

        from epic_0_auth.auth_utils import handle_otp_request, OTP_STORAGE  # pylint: disable=import-outside-toplevel, import-error

        ok, msg = handle_otp_request('u@example.com')
        self.assertTrue(ok)
        # Match current implementation message
        self.assertIn('OTP has been sent', msg)
        self.assertIn('u@example.com', OTP_STORAGE)
        self.assertEqual(len(OTP_STORAGE['u@example.com']), 6)
        self.assertTrue(OTP_STORAGE['u@example.com'].isdigit())

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_request_user_missing(self, mock_get, mock_send):
        """OTP request: missing user returns clear error and no storage."""
        mock_get.return_value = None
        mock_send.return_value = True  # not used when user missing

        from epic_0_auth.auth_utils import handle_otp_request, OTP_STORAGE  # pylint: disable=import-outside-toplevel, import-error

        ok, msg = handle_otp_request('none@example.com')
        self.assertFalse(ok)
        self.assertIn('no account', msg.lower())
        self.assertNotIn('none@example.com', OTP_STORAGE)

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_reset_password_success_flow(self, mock_hash, mock_exec):
        """Password reset: valid OTP -> DB updated -> OTP cleared."""
        mock_hash.return_value = 'new_hash'
        mock_exec.return_value = True

        from epic_0_auth.auth_utils import handle_password_reset, OTP_STORAGE  # pylint: disable=import-outside-toplevel, import-error

        email = 'ok@example.com'
        OTP_STORAGE[email] = '222222'

        ok, msg = handle_password_reset(email, '222222', 'newpw')
        self.assertTrue(ok)
        self.assertIn('successful', msg.lower())
        self.assertNotIn(email, OTP_STORAGE)

    def test_reset_password_bad_otp_flow(self):
        """Password reset: invalid OTP -> clear error -> OTP remains."""
        from epic_0_auth.auth_utils import handle_password_reset, OTP_STORAGE  # pylint: disable=import-outside-toplevel, import-error

        email = 'bad@example.com'
        OTP_STORAGE[email] = '111111'

        ok, msg = handle_password_reset(email, '000000', 'newpw')
        self.assertFalse(ok)
        self.assertIn('invalid', msg.lower())
        self.assertIn(email, OTP_STORAGE)  # still present on failure


if __name__ == '__main__':
    unittest.main()

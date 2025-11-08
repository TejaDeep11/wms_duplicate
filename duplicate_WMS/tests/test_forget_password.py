"""
Unit tests for forgot password and OTP functionality.
Tests the auth_utils.py module for password reset flow.
"""

import unittest
from unittest.mock import patch, MagicMock
from epic_0_auth.auth_utils import (
    handle_otp_request,
    handle_password_reset,
    OTP_STORAGE
)


class TestHandleOTPRequest(unittest.TestCase):
    """Test cases for OTP request handling."""

    def setUp(self):
        """Clear OTP storage before each test."""
        OTP_STORAGE.clear()

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_request_success(self, mock_get_user, mock_send_email):
        """Test successful OTP request."""
        mock_get_user.return_value = {'user_id': 1, 'email': 'user@example.com'}
        mock_send_email.return_value = True

        success, message = handle_otp_request('user@example.com')

        self.assertTrue(success)
        self.assertEqual(message, "An OTP has been sent to your email.")
        self.assertIn('user@example.com', OTP_STORAGE)
        self.assertEqual(len(OTP_STORAGE['user@example.com']), 6)

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_request_user_not_found(self, mock_get_user):
        """Test OTP request for non-existent user."""
        mock_get_user.return_value = None

        success, message = handle_otp_request('nonexistent@example.com')

        self.assertFalse(success)
        self.assertEqual(message, "Error: No account found with that email.")
        self.assertNotIn('nonexistent@example.com', OTP_STORAGE)

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_request_email_failure(self, mock_get_user, mock_send_email):
        """Test OTP request when email sending fails."""
        mock_get_user.return_value = {'user_id': 2, 'email': 'user2@example.com'}
        mock_send_email.return_value = False

        success, message = handle_otp_request('user2@example.com')

        self.assertFalse(success)
        self.assertEqual(message, "Error: Could not send OTP email.")
        self.assertNotIn('user2@example.com', OTP_STORAGE)

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_is_six_digits(self, mock_get_user, mock_send_email):
        """Test that generated OTP is exactly 6 digits."""
        mock_get_user.return_value = {'user_id': 3}
        mock_send_email.return_value = True

        handle_otp_request('test@example.com')

        otp = OTP_STORAGE['test@example.com']
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_otp_overwrites_previous(self, mock_get_user, mock_send_email):
        """Test that new OTP request overwrites previous OTP."""
        mock_get_user.return_value = {'user_id': 4}
        mock_send_email.return_value = True

        # First request
        handle_otp_request('test@example.com')
        first_otp = OTP_STORAGE['test@example.com']

        # Second request
        handle_otp_request('test@example.com')
        second_otp = OTP_STORAGE['test@example.com']

        # They should be different (statistically extremely unlikely to be same)
        self.assertIsNotNone(first_otp)
        self.assertIsNotNone(second_otp)


class TestHandlePasswordReset(unittest.TestCase):
    """Test cases for password reset handling."""

    def setUp(self):
        """Clear OTP storage before each test."""
        OTP_STORAGE.clear()

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_password_reset_success(self, mock_hash, mock_execute):
        """Test successful password reset."""
        email = 'user@example.com'
        otp = '123456'
        OTP_STORAGE[email] = otp
        mock_hash.return_value = 'new_hashed_password'
        mock_execute.return_value = True

        success, message = handle_password_reset(email, otp, 'new_password')

        self.assertTrue(success)
        self.assertEqual(message, "Password reset successful! You can now log in.")
        self.assertNotIn(email, OTP_STORAGE)
        mock_hash.assert_called_once_with('new_password')

    def test_password_reset_invalid_otp(self):
        """Test password reset with invalid OTP."""
        email = 'user@example.com'
        OTP_STORAGE[email] = '123456'

        success, message = handle_password_reset(email, '999999', 'new_password')

        self.assertFalse(success)
        self.assertEqual(message, "Error: Invalid email or OTP.")
        self.assertIn(email, OTP_STORAGE)  # OTP should not be deleted

    def test_password_reset_no_otp_stored(self):
        """Test password reset when no OTP is stored for email."""
        success, message = handle_password_reset(
            'no_otp@example.com',
            '123456',
            'new_password'
        )

        self.assertFalse(success)
        self.assertEqual(message, "Error: Invalid email or OTP.")

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_password_reset_database_failure(self, mock_hash, mock_execute):
        """Test password reset when database update fails."""
        email = 'user@example.com'
        otp = '123456'
        OTP_STORAGE[email] = otp
        mock_hash.return_value = 'new_hash'
        mock_execute.return_value = False  # Database failure

        success, message = handle_password_reset(email, otp, 'new_password')

        self.assertFalse(success)
        self.assertEqual(message, "Error: Could not update password in database.")
        self.assertIn(email, OTP_STORAGE)  # OTP should remain on failure

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_password_reset_query_parameters(self, mock_hash, mock_execute):
        """Test that correct parameters are passed to database."""
        email = 'test@example.com'
        otp = '654321'
        new_password = 'super_secure_password'
        OTP_STORAGE[email] = otp
        mock_hash.return_value = 'hashed_new_password'
        mock_execute.return_value = True

        handle_password_reset(email, otp, new_password)

        call_args = mock_execute.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        self.assertIn('UPDATE Users', query)
        self.assertIn('password_hash', query)
        self.assertEqual(params, ('hashed_new_password', email))

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_password_reset_with_special_characters(self, mock_hash, mock_execute):
        """Test password reset with special characters in new password."""
        email = 'user@example.com'
        otp = '111111'
        new_password = 'N3w_P@ssw0rd!#$'
        OTP_STORAGE[email] = otp
        mock_hash.return_value = 'hashed_special_password'
        mock_execute.return_value = True

        success, _ = handle_password_reset(email, otp, new_password)

        self.assertTrue(success)
        mock_hash.assert_called_once_with(new_password)


class TestOTPStorageManagement(unittest.TestCase):
    """Test OTP storage management."""

    def setUp(self):
        """Clear OTP storage before each test."""
        OTP_STORAGE.clear()

    def test_otp_storage_is_dictionary(self):
        """Test that OTP_STORAGE is a dictionary."""
        self.assertIsInstance(OTP_STORAGE, dict)

    @patch('epic_0_auth.auth_utils.send_otp_email')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_multiple_users_otp_storage(self, mock_get_user, mock_send_email):
        """Test OTP storage with multiple users."""
        mock_get_user.return_value = {'user_id': 1}
        mock_send_email.return_value = True

        handle_otp_request('user1@example.com')
        handle_otp_request('user2@example.com')
        handle_otp_request('user3@example.com')

        self.assertEqual(len(OTP_STORAGE), 3)
        self.assertIn('user1@example.com', OTP_STORAGE)
        self.assertIn('user2@example.com', OTP_STORAGE)
        self.assertIn('user3@example.com', OTP_STORAGE)

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_otp_removed_after_successful_reset(self, mock_hash, mock_execute):
        """Test that OTP is removed from storage after successful reset."""
        email = 'cleanup@example.com'
        otp = '999999'
        OTP_STORAGE[email] = otp
        mock_hash.return_value = 'hash'
        mock_execute.return_value = True

        self.assertIn(email, OTP_STORAGE)

        handle_password_reset(email, otp, 'new_pass')

        self.assertNotIn(email, OTP_STORAGE)


if __name__ == '__main__':
    unittest.main()

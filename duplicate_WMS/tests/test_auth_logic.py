"""
Unit tests for authentication logic.
Tests the auth_utils.py module for login and user retrieval.
"""

import unittest
from unittest.mock import patch, MagicMock
from epic_0_auth.auth_utils import (
    get_user_by_email,
    verify_user_login,
    OTP_STORAGE
)
from epic_0_auth.hash import hash_password


class TestGetUserByEmail(unittest.TestCase):
    """Test cases for get_user_by_email function."""

    @patch('epic_0_auth.auth_utils.fetch_one')
    def test_get_user_by_email_found(self, mock_fetch):
        """Test retrieving an existing user by email."""
        mock_user = {
            'user_id': 1,
            'first_name': 'John',
            'password_hash': 'hashed_password',
            'role_name': 'Admin'
        }
        mock_fetch.return_value = mock_user

        result = get_user_by_email('john@example.com')

        mock_fetch.assert_called_once()
        self.assertEqual(result, mock_user)

    @patch('epic_0_auth.auth_utils.fetch_one')
    def test_get_user_by_email_not_found(self, mock_fetch):
        """Test retrieving a non-existent user."""
        mock_fetch.return_value = None

        result = get_user_by_email('nonexistent@example.com')

        mock_fetch.assert_called_once()
        self.assertIsNone(result)

    @patch('epic_0_auth.auth_utils.fetch_one')
    def test_get_user_by_email_query_structure(self, mock_fetch):
        """Test that correct query parameters are passed."""
        mock_fetch.return_value = None
        email = 'test@example.com'

        get_user_by_email(email)

        call_args = mock_fetch.call_args
        self.assertIn('SELECT', call_args[0][0])
        self.assertEqual(call_args[0][1], (email,))


class TestVerifyUserLogin(unittest.TestCase):
    """Test cases for verify_user_login function."""

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.check_password')
    def test_verify_login_success(self, mock_check_pwd, mock_get_user):
        """Test successful login with correct credentials."""
        mock_user = {
            'user_id': 1,
            'first_name': 'Alice',
            'password_hash': 'hashed_password',
            'role_name': 'Manager'
        }
        mock_get_user.return_value = mock_user
        mock_check_pwd.return_value = True

        result = verify_user_login('alice@example.com', 'correct_password')

        self.assertEqual(result, mock_user)
        mock_check_pwd.assert_called_once_with('correct_password', 'hashed_password')

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_verify_login_user_not_found(self, mock_get_user):
        """Test login with non-existent email."""
        mock_get_user.return_value = None

        result = verify_user_login('nonexistent@example.com', 'password')

        self.assertEqual(result, "Error: User not found.")

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.check_password')
    def test_verify_login_wrong_password(self, mock_check_pwd, mock_get_user):
        """Test login with incorrect password."""
        mock_user = {
            'user_id': 2,
            'first_name': 'Bob',
            'password_hash': 'hashed_password',
            'role_name': 'Employee'
        }
        mock_get_user.return_value = mock_user
        mock_check_pwd.return_value = False

        result = verify_user_login('bob@example.com', 'wrong_password')

        self.assertEqual(result, "Error: Incorrect password.")

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.check_password')
    def test_verify_login_with_special_characters(self, mock_check_pwd, mock_get_user):
        """Test login with special characters in password."""
        mock_user = {
            'user_id': 3,
            'first_name': 'Charlie',
            'password_hash': hash_password('P@ssw0rd!'),
            'role_name': 'User'
        }
        mock_get_user.return_value = mock_user
        mock_check_pwd.return_value = True

        result = verify_user_login('charlie@example.com', 'P@ssw0rd!')

        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 3)


class TestAuthenticationIntegration(unittest.TestCase):
    """Integration tests for authentication flow."""

    @patch('epic_0_auth.auth_utils.fetch_one')
    @patch('epic_0_auth.auth_utils.check_password')
    def test_full_login_flow(self, mock_check_pwd, mock_fetch):
        """Test complete login flow from email to verification."""
        mock_user = {
            'user_id': 5,
            'first_name': 'Diana',
            'password_hash': 'hashed_pass',
            'role_name': 'Admin'
        }
        mock_fetch.return_value = mock_user
        mock_check_pwd.return_value = True

        result = verify_user_login('diana@example.com', 'password123')

        self.assertEqual(result['first_name'], 'Diana')
        self.assertEqual(result['role_name'], 'Admin')

    def test_otp_storage_initialization(self):
        """Test that OTP_STORAGE is properly initialized."""
        self.assertIsInstance(OTP_STORAGE, dict)


if __name__ == '__main__':
    unittest.main()

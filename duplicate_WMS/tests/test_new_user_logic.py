"""
Unit tests for new user registration logic.
Tests the auth_utils.py module for user registration functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from epic_0_auth.auth_utils import register_new_user


class TestRegisterNewUser(unittest.TestCase):
    """Test cases for new user registration."""

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_new_user_success(self, mock_hash, mock_get_user, mock_execute):
        """Test successful new user registration."""
        mock_get_user.return_value = None  # User doesn't exist
        mock_hash.return_value = 'hashed_password_123'
        mock_execute.return_value = 1  # Simulating user_id returned

        success, message = register_new_user(
            'newuser@example.com',
            'John',
            'Doe',
            '1234567890',
            'password123',
            2
        )

        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully!")
        mock_hash.assert_called_once_with('password123')
        mock_execute.assert_called_once()

    @patch('epic_0_auth.auth_utils.get_user_by_email')
    def test_register_existing_user(self, mock_get_user):
        """Test registration with existing email."""
        mock_get_user.return_value = {
            'user_id': 1,
            'email': 'existing@example.com'
        }

        success, message = register_new_user(
            'existing@example.com',
            'Jane',
            'Smith',
            '9876543210',
            'password456',
            3
        )

        self.assertFalse(success)
        self.assertEqual(message, "Error: An account with this email already exists.")

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_database_failure(self, mock_hash, mock_get_user, mock_execute):
        """Test registration when database insert fails."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'hashed_password'
        mock_execute.return_value = None  # Simulating database failure

        success, message = register_new_user(
            'newuser@example.com',
            'Alice',
            'Johnson',
            '5555555555',
            'securepass',
            1
        )

        self.assertFalse(success)
        self.assertEqual(message, "Error: Could not create account.")

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_with_special_characters_in_name(
            self, mock_hash, mock_get_user, mock_execute):
        """Test registration with special characters in names."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'hashed_pass'
        mock_execute.return_value = 10

        success, message = register_new_user(
            'special@example.com',
            "O'Brien",
            'José-María',
            '1112223333',
            'password',
            2
        )

        self.assertTrue(success)
        self.assertEqual(message, "Account created successfully!")

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_all_role_ids(self, mock_hash, mock_get_user, mock_execute):
        """Test registration with different role IDs."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'hashed'
        mock_execute.return_value = 1

        for role_id in [1, 2, 3, 4, 5]:
            success, _ = register_new_user(
                f'user{role_id}@example.com',
                'First',
                'Last',
                '1234567890',
                'password',
                role_id
            )
            self.assertTrue(success)

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_query_parameters(self, mock_hash, mock_get_user, mock_execute):
        """Test that correct parameters are passed to database."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'test_hash'
        mock_execute.return_value = 5

        register_new_user(
            'test@example.com',
            'Test',
            'User',
            '9999999999',
            'testpass',
            2
        )

        call_args = mock_execute.call_args
        params = call_args[0][1]

        self.assertEqual(params[0], 2)  # role_id
        self.assertEqual(params[1], 'Test')  # first_name
        self.assertEqual(params[2], 'User')  # last_name
        self.assertEqual(params[3], 'test@example.com')  # email
        self.assertEqual(params[4], 'test_hash')  # password_hash
        self.assertEqual(params[5], '9999999999')  # phone


class TestNewUserEdgeCases(unittest.TestCase):
    """Test edge cases for user registration."""

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_with_empty_last_name(self, mock_hash, mock_get_user, mock_execute):
        """Test registration with empty last name."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'hash'
        mock_execute.return_value = 1

        success, _ = register_new_user(
            'user@example.com',
            'SingleName',
            '',
            '1234567890',
            'password',
            1
        )

        self.assertTrue(success)

    @patch('epic_0_auth.auth_utils.execute_query')
    @patch('epic_0_auth.auth_utils.get_user_by_email')
    @patch('epic_0_auth.auth_utils.hash_password')
    def test_register_with_long_names(self, mock_hash, mock_get_user, mock_execute):
        """Test registration with very long names."""
        mock_get_user.return_value = None
        mock_hash.return_value = 'hash'
        mock_execute.return_value = 1

        long_name = 'A' * 100

        success, _ = register_new_user(
            'longname@example.com',
            long_name,
            long_name,
            '1234567890',
            'password',
            1
        )

        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()

"""
Unit tests for password hashing functions.
Tests the hash.py module for secure password handling.
"""

import unittest
from unittest.mock import patch
import bcrypt
from epic_0_auth.hash import hash_password, check_password


class TestPasswordHashing(unittest.TestCase):
    """Test cases for password hashing and verification."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password_123"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)

    def test_hash_password_not_equal_to_plain(self):
        """Test that hashed password is different from plain text."""
        password = "my_secret_password"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)

    def test_hash_password_different_each_time(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "same_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertNotEqual(hash1, hash2)

    def test_check_password_correct(self):
        """Test that correct password verification returns True."""
        password = "correct_password"
        hashed = hash_password(password)
        result = check_password(password, hashed)
        self.assertTrue(result)

    def test_check_password_incorrect(self):
        """Test that incorrect password verification returns False."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        result = check_password(wrong_password, hashed)
        self.assertFalse(result)

    def test_check_password_empty_string(self):
        """Test password check with empty string."""
        password = "test_password"
        hashed = hash_password(password)
        result = check_password("", hashed)
        self.assertFalse(result)

    def test_check_password_with_special_characters(self):
        """Test password hashing with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        result = check_password(password, hashed)
        self.assertTrue(result)

    def test_check_password_with_unicode(self):
        """Test password hashing with unicode characters."""
        password = "पासवर्ड123"
        hashed = hash_password(password)
        result = check_password(password, hashed)
        self.assertTrue(result)

    def test_check_password_invalid_hash_format(self):
        """Test check_password with invalid hash format."""
        password = "test_password"
        invalid_hash = "not_a_valid_hash"
        result = check_password(password, invalid_hash)
        self.assertFalse(result)

    def test_check_password_exception_handling(self):
        """Test that exceptions in check_password return False."""
        with patch('bcrypt.checkpw', side_effect=Exception("Test error")):
            result = check_password("test", "hash")
            self.assertFalse(result)

    def test_hash_password_length(self):
        """Test that hashed password has expected bcrypt length."""
        password = "test"
        hashed = hash_password(password)
        # Bcrypt hashes are 60 characters long
        self.assertEqual(len(hashed), 60)

    def test_hash_password_starts_with_bcrypt_identifier(self):
        """Test that hash starts with bcrypt version identifier."""
        password = "test_password"
        hashed = hash_password(password)
        self.assertTrue(hashed.startswith('$2b$'))


class TestPasswordEdgeCases(unittest.TestCase):
    """Test edge cases for password hashing."""

    def test_very_long_password(self):
        """Test hashing of very long passwords."""
        password = "a" * 1000
        hashed = hash_password(password)
        self.assertTrue(check_password(password, hashed))

    def test_password_with_null_bytes_raises_error(self):
        """Test that bcrypt raises ValueError for null bytes in password."""
        # Bcrypt explicitly disallows null bytes for security reasons
        # This test verifies that the library correctly rejects such input
        with self.assertRaises(ValueError):
            hash_password("pass\x00word")

    def test_single_character_password(self):
        """Test single character password."""
        password = "a"
        hashed = hash_password(password)
        self.assertTrue(check_password(password, hashed))

    def test_password_with_spaces(self):
        """Test password containing spaces."""
        password = "my pass word with spaces"
        hashed = hash_password(password)
        self.assertTrue(check_password(password, hashed))

    def test_password_with_tabs_and_newlines(self):
        """Test password containing whitespace characters."""
        password = "pass\t\nword"
        hashed = hash_password(password)
        self.assertTrue(check_password(password, hashed))


class TestPasswordHashingConsistency(unittest.TestCase):
    """Test consistency of password hashing across multiple operations."""

    def test_hash_verify_cycle(self):
        """Test multiple hash-verify cycles with same password."""
        password = "test_cycle_password"
        for _ in range(5):
            hashed = hash_password(password)
            self.assertTrue(check_password(password, hashed))

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        passwords = ["password1", "password2", "password3"]
        hashes = [hash_password(pwd) for pwd in passwords]
        
        # All hashes should be unique
        self.assertEqual(len(hashes), len(set(hashes)))

    def test_case_sensitive_password(self):
        """Test that passwords are case-sensitive."""
        password = "MyPassword"
        different_case = "mypassword"
        hashed = hash_password(password)
        
        self.assertTrue(check_password(password, hashed))
        self.assertFalse(check_password(different_case, hashed))


if __name__ == '__main__':
    unittest.main()

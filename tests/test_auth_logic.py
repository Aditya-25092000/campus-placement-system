"""Unit tests for Werkzeug authentication and password hashing."""
import unittest
from werkzeug.security import generate_password_hash, check_password_hash


class TestAuthenticationSecurity(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        password = 'admin123'
        hashed = generate_password_hash(password)
        
        # Verify plain password is not stored
        self.assertNotEqual(password, hashed)
        self.assertTrue(hashed.startswith(('scrypt:', 'pbkdf2:')))
        
        # Verify correct verification
        self.assertTrue(check_password_hash(hashed, 'admin123'))
        
        # Verify incorrect rejection
        self.assertFalse(check_password_hash(hashed, 'wrongpassword'))
        self.assertFalse(check_password_hash(hashed, ''))


if __name__ == '__main__':
    unittest.main()

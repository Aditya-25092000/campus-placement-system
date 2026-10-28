"""Unit and integration tests for Flask application structure and routes."""
import unittest
from unittest.mock import patch
from app import create_app


class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        # Prevent seed_admin from trying to connect to real db during setup
        with patch('services.auth_service.seed_admin'):
            self.app = create_app()
            self.app.config['TESTING'] = True
            self.app.config['SECRET_KEY'] = 'test-secret'
            self.client = self.app.test_client()

    def test_unauthenticated_access_redirects_to_login(self):
        """Unauthenticated requests to protected endpoints must redirect to login."""
        endpoints = [
            '/',
            '/dashboard',
            '/students/',
            '/companies/',
            '/jobs/',
            '/applications/',
            '/offers/',
            '/eligibility/',
            '/reports/',
            '/showcase/'
        ]
        for ep in endpoints:
            response = self.client.get(ep, follow_redirects=False)
            self.assertEqual(response.status_code, 302, f"Expected 302 for {ep}")
            self.assertIn('/login', response.headers.get('Location', ''))

    def test_login_page_loads_publicly(self):
        """Login page must be publicly accessible (200 OK)."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Campus Placement System', response.data)
        self.assertIn(b'Sign in to manage placements', response.data)

    def test_404_page(self):
        """Non-existent routes should return 404 or redirect."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_name'] = 'Admin'

        response = self.client.get('/this-path-does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404', response.data)

    def test_logout_clears_session(self):
        """Logging out should clear session and redirect to /login."""
        with self.client.session_transaction() as sess:
            sess['admin_id'] = 1
            sess['admin_name'] = 'Admin'

        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers.get('Location', ''))


if __name__ == '__main__':
    unittest.main()

# test_app.py
import unittest
from app import app
from models import db, User
from testfixtures import TempDirectory
from flask_testing import TestCase
from flask import json

class FlaskTestCase(TestCase):
    def create_app(self):
        return app

    def setUp(self):
        self.db_fd, db.Model.metadata.create_all(db.engine)

    def tearDown(self):
        db.Model.metadata.drop_all(db.engine)

    def test_user_registration(self):
        with self.client:
            response = self.client.post('/register', data=json.dumps({'email': 'test@example.com', 'password': 'password'}), content_type='application/json')
            self.assertEqual(response.status_code, 201)
            self.assertTrue(User.query.filter_by(email='test@example.com').first())

    def test_user_registration_duplicate_email(self):
        with self.client:
            self.client.post('/register', data=json.dumps({'email': 'test@example.com', 'password': 'password'}), content_type='application/json')
            response = self.client.post('/register', data=json.dumps({'email': 'test@example.com', 'password': 'password'}), content_type='application/json')
            self.assertEqual(response.status_code, 409)

    def test_user_login(self):
        with self.client:
            self.client.post('/register', data=json.dumps({'email': 'test@example.com', 'password': 'password'}), content_type='application/json')
            response = self.client.post('/login', data=json.dumps({'email': 'test@example.com', 'password': 'password'}), content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertIn('access_token', response.json)

    def test_user_login_invalid_credentials(self):
        with self.client:
            response = self.client.post('/login', data=json.dumps({'email': 'test@example.com', 'password': 'wrongpassword'}), content_type='application/json')
            self.assertEqual(response.status_code, 401)

    def test_error_handling(self):
        with self.client:
            response = self.client.get('/nonexistent')
            self.assertEqual(response.status_code, 404)
            self.assertIn('error', response.json)

class TokenTestCase(unittest.TestCase):
    def test_generate_token(self):
        from token_service import generate_token
        token = generate_token(1)
        self.assertIsNotNone(token)

    def test_verify_token(self):
        from token_service import generate_token, verify_token
        token = generate_token(1)
        payload = verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload, 1)

    def test_verify_token_invalid(self):
        from token_service import verify_token
        payload = verify_token('invalidtoken')
        self.assertIsNone(payload)

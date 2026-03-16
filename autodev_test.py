import unittest
from app import app, db
from models import User
from token_service import TokenService
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        with app.test_client() as client:
            response = client.post('/register', json={'username': 'testuser', 'password': 'testpass'})
            self.assertEqual(response.status_code, 201)
            self.assertTrue('message' in response.json)

    def test_user_registration_missing_data(self):
        with app.test_client() as client:
            response = client.post('/register', json={})
            self.assertEqual(response.status_code, 400)
            self.assertTrue('message' in response.json)

    def test_user_login(self):
        with app.test_client() as client:
            client.post('/register', json={'username': 'testuser', 'password': 'testpass'})
            response = client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
            self.assertEqual(response.status_code, 200)
            self.assertTrue('token' in response.json)

    def test_user_login_incorrect_password(self):
        with app.test_client() as client:
            client.post('/register', json={'username': 'testuser', 'password': 'testpass'})
            response = client.post('/login', json={'username': 'testuser', 'password': 'wrongpass'})
            self.assertEqual(response.status_code, 401)

    def test_token_validation(self):
        with app.test_client() as client:
            client.post('/register', json={'username': 'testuser', 'password': 'testpass'})
            response = client.post('/login', json={'username': 'testuser', 'password': 'testpass'})
            token = response.json['token']
            response = client.get('/register', headers={'Authorization': token})
            self.assertEqual(response.status_code, 403)

    def test_token_validation_invalid_token(self):
        with app.test_client() as client:
            response = client.get('/register', headers={'Authorization': 'invalid_token'})
            self.assertEqual(response.status_code, 403)

    def test_error_handling(self):
        with app.test_client() as client:
            response = client.post('/register', json={'username': 'testuser'})
            self.assertEqual(response.status_code, 400)
            self.assertTrue('message' in response.json)

if __name__ == '__main__':
    unittest.main()
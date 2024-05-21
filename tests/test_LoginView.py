
import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.create_test_user()

    def tearDown(self):
        pass

    def clear_database(self):
        response = requests.get(BASE_URL + 'clear_db/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'All data cleared successfully'})

    def create_test_user(self):
        requests.post(BASE_URL + 'user/create/', data={'username': 'test_user', 'password': 'test_password', 'email': 'test@example.com'})

    def test_login_without_data(self):
        response = requests.post(BASE_URL + 'login/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'error': 'Invalid credentials'})

    def test_login_without_username(self):
        response = requests.post(BASE_URL + 'login/', data={'password': 'test_password'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'error': 'Invalid credentials'})

    def test_login_without_password(self):
        response = requests.post(BASE_URL + 'login/', data={'username': 'test_user'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'error': 'Invalid credentials'})

    def test_logout_success(self):
        response = requests.post(BASE_URL + 'login/', data={'username': 'test_user', 'password': 'test_password'})
        token = response.json().get('token')
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 40)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
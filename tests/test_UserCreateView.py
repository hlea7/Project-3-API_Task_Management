
import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class TestUserCreation(unittest.TestCase):
    def setUp(self):
        self.clear_database()

    def tearDown(self):
        pass

    def clear_database(self):
        response = requests.get(BASE_URL + 'clear_db/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'All data cleared successfully'})

    def test_create_user_missing_all_fields(self):
        response = requests.post(BASE_URL + 'user/create/', data={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username, password, and email are required'})

    def test_create_user_missing_username_fields(self):
        response = requests.post(BASE_URL + 'user/create/', data={'password': 'test_password', 'email': 'test@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username, password, and email are required'})

    def test_create_user_missing_password_fields(self):
        response = requests.post(BASE_URL + 'user/create/', data={'username': 'test_user', 'email': 'test@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username, password, and email are required'})

    def test_create_user_missing_email_fields(self):
        response = requests.post(BASE_URL + 'user/create/', data={'username': 'test_user', 'password': 'test_password'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Username, password, and email are required'})

    def test_create_user_success(self):
        username = "test_user"
        email = 'test@example.com'
        response = requests.post(BASE_URL + 'user/create/', data={'username': username, 'password': 'test_password', 'email': email})
        new_user = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(new_user.get('username'), username)
        self.assertEqual(new_user.get('email'), email)

if __name__ == '__main__':
    unittest.main()

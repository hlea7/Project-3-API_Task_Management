
import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class TestLogoutView(unittest.TestCase):
    def setUp(self):
        self.clear_database()

    def tearDown(self):
        pass

    def clear_database(self):
        response = requests.get(BASE_URL + 'clear_db/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'All data cleared successfully'})

    def test_logout_without_token(self):
        response = requests.post(BASE_URL + 'logout/')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_logout_wrong_token(self):
        token = "wrong_token"
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(BASE_URL + 'logout/', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Invalid token.'})

    def test_logout_success(self):
        self.clear_database()
        requests.post(BASE_URL + 'user/create/', data={'username': 'test_user', 'password': 'test_password', 'email': 'test@example.com'})
        response = requests.post(BASE_URL + 'login/', data={'username': 'test_user', 'password': 'test_password'})
        token = response.json().get('token')
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(BASE_URL + 'logout/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Successfully logged out'})

if __name__ == '__main__':
    unittest.main()

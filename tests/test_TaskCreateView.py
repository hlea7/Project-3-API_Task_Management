import unittest
import requests
from datetime import datetime, timedelta
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class TestTaskCreateView(unittest.TestCase):

    def setUp(self):
        self.clear_database()

    def tearDown(self):
        self.clear_database()

    def clear_database(self):
        response = requests.get(BASE_URL + 'clear_db/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'All data cleared successfully'})

    def create_test_users(self):
        result = []
        result.append(self.create_user('creator_user', 'creator_password', 'creator@example.com'))
        result.append(self.create_user('executor_user', 'executor_password', 'executor@example.com'))
        return result
        
    def create_user(self, username, password, email):
        response = requests.post(BASE_URL + 'user/create/', data={
            'username': username,
            'password': password,
            'email': email
        })
        self.assertEqual(response.status_code, 201)
        return response.json().get('id')
    
    def login_user(self, username, password):
        response = requests.post(BASE_URL + 'login/', data={
            'username': username,
            'password': password
        })
        self.assertEqual(response.status_code, 200)
        token = response.json().get('token')
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 40)
        return token

    def test_create_task_success(self):
        self.clear_database()
        result = self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        

        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={
            'executor': result[1], 
            'name': 'Test Task',
            'cost': 100,
            'deadline': deadline
        })
        self.assertEqual(response.status_code, 201)
        response_data = response.json()

        self.assertEqual(response_data['name'], 'Test Task')
        self.assertEqual(response_data['cost'], '100.00')
        self.assertEqual(response_data['executor'], result[1])

    def test_create_task_creator_as_executor(self):
        self.clear_database()
        result = self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={
            'executor': result[0],  # assuming creator_user has ID 1
            'name': 'Test Task',
            'cost': 100,
            'deadline': deadline
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'The creator of a task cannot be its executor'})

    def test_create_task_non_existent_executor(self):
        self.clear_database()
        self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={
            'executor': 999,  # non-existent user ID
            'name': 'Test Task',
            'cost': 100,
            'deadline': deadline
        })
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertEqual(response_data['name'], 'Test Task')
        self.assertEqual(response_data['cost'], '100.00')
        self.assertIsNone(response_data.get('executor'))

    def test_create_task_missing_fields(self):
        self.clear_database()
        self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={})
        self.assertEqual(response.status_code, 400)
        response_data = response.json()

        self.assertIn('name', response_data)
        self.assertIn('cost', response_data)
        self.assertIn('deadline', response_data)

    def test_create_task_invalid_cost(self):
        self.clear_database()
        result = self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        deadline = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')
        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={
            'executor': result[1],  # assuming executor_user has ID 2
            'name': 'Test Task',
            'cost': 'invalid',  # invalid cost
            'deadline': deadline
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('cost', response.json())

    def test_create_task_invalid_deadline(self):
        self.clear_database()
        result = self.create_test_users()
        token = self.login_user('creator_user', 'creator_password')
        headers = {'Authorization': f'Token {token}'}
        response = requests.post(BASE_URL + 'task/create/', headers=headers, json={
            'executor': result[1],  # assuming executor_user has ID 2
            'name': 'Test Task',
            'cost': 100,
            'deadline': 'invalid-date'  # invalid deadline
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('deadline', response.json())

if __name__ == '__main__':
    unittest.main()

import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class TasksCreatedByUserTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.user_id = self.create_user('test_user', 'test_password', 'test_user@example.com')
        self.token = self.login_user('test_user', 'test_password')
        self.headers = {'Authorization': f'Token {self.token}'}

    def tearDown(self):
        self.clear_database()

    def clear_database(self):
        response = requests.get(BASE_URL + 'clear_db/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'All data cleared successfully'})

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

    def create_task(self, name, cost, deadline):
        response = requests.post(BASE_URL + 'task/create/', headers=self.headers, json={
            'name': name,
            'cost': cost,
            'deadline': deadline
        })
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_get_tasks_created_by_user(self):
        task_data = {
            'name': 'Test Task',
            'cost': 100,
            'deadline': '2024-06-01'  # Assuming a valid deadline date
        }
        self.create_task(**task_data)

        response = requests.get(BASE_URL + 'tasks-created-by-user/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        tasks = response.json()
        self.assertEqual(len(tasks), 1)  # Assuming only one task is created
        self.assertEqual(tasks[0]['name'], 'Test Task')
        self.assertEqual(tasks[0]['creator'], self.user_id)
        self.assertEqual(tasks[0]['cost'], '100.00')
        self.assertEqual(tasks[0]['deadline'], '2024-06-01')

    def test_unauthorized_access(self):
        response = requests.get(BASE_URL + 'tasks-created-by-user/')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()

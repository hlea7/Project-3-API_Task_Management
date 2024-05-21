import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class UnassignedTasksAPIViewTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.user_id = self.create_user('test_user', 'test_password', 'test_user@example.com')
        self.executor_id = self.create_user('executor_user', 'executor_password', 'executor@example.com')
        self.token = self.login_user('test_user', 'test_password')
        self.headers = {'Authorization': f'Token {self.token}'}
        self.task_id = self.create_task('Unassigned Task', 100, '2024-06-01', None)
        self.task_id2 = self.create_task('Another Unassigned Task', 150, '2024-06-10', None)
        self.task_id3 = self.create_task('Assigned Task', 200, '2024-05-01', self.executor_id)

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

    def create_task(self, name, cost, deadline, executor_id):
        response = requests.post(BASE_URL + 'task/create/', headers=self.headers, json={
            'name': name,
            'cost': cost,
            'deadline': deadline,
            'executor': executor_id
        })
        self.assertEqual(response.status_code, 201)
        return response.json().get('id')

    def test_unassigned_tasks_api_view(self):
        response = requests.get(BASE_URL + 'unassigned-tasks/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        tasks = response.json()
        self.assertEqual(len(tasks), 2) 
        self.assertEqual(tasks[0]['name'], 'Unassigned Task')
        self.assertEqual(tasks[0]['cost'], '100.00')
        self.assertEqual(tasks[1]['name'], 'Another Unassigned Task')
        self.assertEqual(tasks[1]['cost'], '150.00')
        self.assertLess(tasks[0]['cost'], tasks[1]['cost']) 

if __name__ == '__main__':
    unittest.main()

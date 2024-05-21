import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class BecomeExecutorAPIViewTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.user_id = self.create_user('test_user', 'test_password', 'test_user@example.com')
        self.executor_id = self.create_user('executor_user', 'executor_password', 'executor@example.com')
        self.token = self.login_user('test_user', 'test_password')
        self.headers = {'Authorization': f'Token {self.token}'}
        self.task_id = self.create_task('Unassigned Task', 100, '2024-06-01', None)
        self.task_id2 = self.create_task('Assigned Task', 150, '2024-06-10', self.executor_id)
        self.token_1 = self.login_user('executor_user', 'executor_password')
        self.headers_1 = {'Authorization': f'Token {self.token_1}'}


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

    def test_become_executor_success(self):
        response = requests.patch(BASE_URL + f'become-executor/{self.task_id}/', headers=self.headers_1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'You have been assigned as the executor of the task'})

    def test_become_executor_task_not_found(self):
        response = requests.patch(BASE_URL + 'become-executor/999/', headers=self.headers_1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Task not found'})

    def test_become_executor_own_task(self):
        response = requests.patch(BASE_URL + f'become-executor/{self.task_id2}/', headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'You cannot assign yourself as executor of your own task'})

    def test_become_executor_already_assigned(self):
        response = requests.patch(BASE_URL + f'become-executor/{self.task_id2}/', headers=self.headers_1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'This task already has an executor'})

if __name__ == '__main__':
    unittest.main()

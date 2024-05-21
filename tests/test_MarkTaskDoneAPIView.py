import unittest
import requests
import json 
import os

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class MarkTaskDoneAPIViewTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.user_id = self.create_user('test_user', 'test_password', 'test_user@example.com')
        self.executor_id = self.create_user('executor_user', 'executor_password', 'executor@example.com')
        self.token = self.login_user('test_user', 'test_password')
        self.executor_token = self.login_user('executor_user', 'executor_password')
        self.headers = {'Authorization': f'Token {self.token}'}
        self.executor_headers = {'Authorization': f'Token {self.executor_token}'}
        self.task_id = self.create_task('Assigned Task', 100, '2024-06-01', self.executor_id)
        self.unassigned_task_id = self.create_task('Unassigned Task', 150, '2024-06-10', None)

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

    def test_mark_task_done_success(self):
        response = requests.patch(BASE_URL + f'mark-task-done/{self.task_id}/', headers=self.executor_headers)
        self.assertEqual(response.status_code, 200)
        
        task_data = response.json()
        self.assertTrue(task_data['is_done'])

    def test_mark_task_done_task_not_found(self):
        response = requests.patch(BASE_URL + 'mark-task-done/999/', headers=self.executor_headers)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Task not found'})

    def test_mark_task_done_not_authorized(self):
        response = requests.patch(BASE_URL + f'mark-task-done/{self.task_id}/', headers=self.headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'You are not authorized to mark this task as done'})

    def test_mark_task_done_unassigned_task(self):
        response = requests.patch(BASE_URL + f'mark-task-done/{self.unassigned_task_id}/', headers=self.executor_headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'error': 'You are not authorized to mark this task as done'})

if __name__ == '__main__':
    unittest.main()
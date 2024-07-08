import unittest
import requests
import json 
import os
from datetime import datetime, timedelta

def get_url():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, "r") as f:
        return json.load(f)['BASE_URL']


BASE_URL = get_url()

class UserTasksStatsAPIViewTestCase(unittest.TestCase):
    def setUp(self):
        self.clear_database()
        self.user_id = self.create_user('test_user', 'test_password', 'test_user@example.com')
        self.executor_id = self.create_user('executor_user', 'executor_password', 'executor@example.com')

        self.token = self.login_user('executor_user', 'executor_password')
        self.headers = {'Authorization': f'Token {self.token}'}

        current_date = datetime.now()

        overdue_date1 = (current_date - timedelta(days=30)).strftime('%Y-%m-%d')
        overdue_date2 = (current_date - timedelta(days=45)).strftime('%Y-%m-%d')
        overdue_date3 = (current_date - timedelta(days=60)).strftime('%Y-%m-%d')

        future_date1 = (current_date + timedelta(days=10)).strftime('%Y-%m-%d')
        future_date2 = (current_date + timedelta(days=20)).strftime('%Y-%m-%d')
        future_date3 = (current_date + timedelta(days=25)).strftime('%Y-%m-%d')
        future_date4 = (current_date + timedelta(days=5)).strftime('%Y-%m-%d')
        self.task_id6 = self.create_task('Spent Task', 50, future_date1, self.user_id)
        self.task_id7 = self.create_task('Spent Task', 150, future_date2, self.user_id, True)

        self.token = self.login_user('test_user', 'test_password')
        self.headers = {'Authorization': f'Token {self.token}'}
        self.task_id = self.create_task('Completed Task', 100, overdue_date1, self.executor_id, True)
        self.task_id2 = self.create_task('Pending Task', 150, future_date3, self.executor_id, False)
        self.task_id3 = self.create_task('Overdue Task', 200, overdue_date2, self.executor_id, False)
        self.task_id4 = self.create_task('Assigned Task', 300, future_date4, self.executor_id)
        self.task_id5 = self.create_task('Another Completed Task', 250, overdue_date3, self.executor_id, True)

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

    def create_task(self, name, cost, deadline, executor_id, is_done=False):
        response = requests.post(BASE_URL + 'task/create/', headers=self.headers, json={
            'name': name,
            'cost': cost,
            'deadline': deadline,
            'executor': executor_id, 
            "is_done": is_done
        })
        self.assertEqual(response.status_code, 201)
        return response.json().get('id')

    def test_user_tasks_stats_api_view(self):
        response = requests.get(BASE_URL + 'user-tasks-stats/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        stats_data = response.json()
        self.assertEqual(stats_data['completed_tasks'], 2)
        self.assertEqual(stats_data['pending_tasks'], 3)
        self.assertEqual(stats_data['overdue_tasks'], 1)
        self.assertEqual(stats_data['assigned_tasks'], 2)
        self.assertEqual(stats_data['total_earned'], 150)
        self.assertEqual(stats_data['total_spent'], 1000)

if __name__ == '__main__':
    unittest.main()
### Django Task Management System API

---

#### Models

##### Task Model
- `creator`: Stores information about the creator of the task. Reference to the built-in User model.
- `executor`: Stores information about the executor of the task. Reference to the built-in User model. Can be empty.
- `name`: The name of the task with a maximum length of 255 characters.
- `cost`: The cost of the task. A decimal number with 8 digits in total and 2 decimal places.
- `is_done`: The status of task completion. A boolean value.
- `deadline`: The deadline for task completion.

---

#### Views

##### [First student's tasks]

##### UserCreateView
This view allows for the creation of a user.

1. Implement the `post` method to handle POST requests for creating a new user.
2. Check for the presence of: `username`, `password`, and `email`. If any of these values are missing in the request body, return an error message `{'error': 'Username, password, and email are required'}` with the status code `400 BAD REQUEST`.
3. Check if a user with the specified `username` already exists. If a user with this username already exists, return an error message `{'error': 'Username already exists'}` with the status code `400 BAD REQUEST`.
4. If all data is valid, create a new user. Upon successful creation of the user, return a user data (id, username, email) in JSON format with the status code `201 CREATED`.

Hint: To work with the `User` model and send HTTP responses, use the appropriate functions from Django REST Framework: `User.objects.create_user`, `Response`.

##### LoginView
This view allows a user to authenticate and receive a token.

1. Implement the `post` method to handle POST requests for user authentication.
2. Retrieve the `username` and `password` from the request. Attempt to authenticate the user.
3. If authentication is successful and the user exists, log the user into the system. Create or retrieve the user's authentication token using the `Token` model. If the token is successfully created or retrieved, return it in the response `{'token': <token value>}` with the status code `200 OK`.
4. If authentication fails or incorrect data is provided, return an error message `{'error': 'Invalid credentials'}` with the status code `401 UNAUTHORIZED`.

##### LogoutView
This view allows for the deletion of a user's token.

1. Only authenticated users can use this view.
2. Implement the `post` method to handle POST requests for logging the user out.
3. Delete the user's authentication token.
4. Return a message indicating successful logout `{'message': 'Successfully logged out'}` with the status code `200 OK` if the token is successfully deleted.

##### TaskCreateView
This view allows for the creation of a new task.

1. Define the `post` method to handle POST requests.
2. The creator of the task is specified as the current authenticated user.
3. If the current user is specified as the executor, return an error message `{'error': 'The creator of a task cannot be its executor'}` with the status code 400 (HTTP_400_BAD_REQUEST).
4. If the data includes an executor, check if a user with the given executor_id exists. If a user with this executor_id does not exist, set the executor to None.
5. Create a task with the resulting data and return the created task's data with the status code 201 (HTTP_201_CREATED).
6. If the data is invalid, return validation errors (serializer.errors) with the status code 400 (HTTP_400_BAD_REQUEST).

Required fields for the request: executor, name, cost, deadline.

##### TasksCreatedByUser
This view allows displaying the tasks created by the current user.

1. Only authenticated users can use this view.
2. This view should return a complete description of all tasks created by the user in the form of a list.

Fields for each task: executor, name, cost, deadline.

##### TaskWithExecutorAPIView
This view allows displaying all existing tasks.

1. This view should return a list of all tasks.
2. If a task does not have an executor specified, the JSON should have "undefined" as the value for the executor.

Fields for each task: executor, name, cost, deadline.

##### [Second student's tasks]

##### UserTasksAPIView
This view allows displaying all tasks of the current user.

1. Only authenticated users can use this view.
2. This view should return all tasks where the current user is specified as the executor.

Fields for each task: executor, name, cost, deadline.

##### UserTasksStatsAPIView
This view allows displaying statistics for the tasks of the current user.

1. Only authenticated users can use this view.
2. The `get` method should return the following statistics in JSON format:
   - Number of completed tasks (key: `completed_tasks`)
   - Number of pending tasks (key: `pending_tasks`)
   - Number of overdue tasks (key: `overdue_tasks`)
   - Number of tasks assigned to the user (key: `assigned_tasks`)
   - Total amount earned: The sum of the cost of all tasks completed by this user (key: `total_earned`)
   - Total amount spent: The sum of the cost of all tasks assigned by this user (key: `total_spent`)
3. The values for `total_earned` and `total_spent` should be 0 if there are no corresponding tasks (handle None values).
4. The response should be returned in JSON format with a status code of 200 OK.

Example result: `{'completed_tasks': 0, 'pending_tasks': 5, 'overdue_tasks': 0, 'assigned_tasks': 1, 'total_earned': 0, 'total_spent': 6000.0}`

##### UnassignedTasksAPIView
This view should display all tasks without an assigned executor.

1. Only authenticated users can use this view.
2. The `get` method should return a list of tasks without an assigned executor.
3. The tasks should be sorted by cost in ascending order.
4. The response should be returned in JSON format with a status code of 200 OK.

Fields for each task: executor, name, cost, deadline.

##### BecomeExecutorAPIView
This view allows the user to become the executor of the task.

1. Only authenticated users can use this view.
2. The view should implement the `patch` method, which receives the task identifier through the URL.
3. If the task is not found, return an error message `{'error': 'Task not found'}` with the status code `404 Not Found`.
4. If the current user is the creator of the task, return an error message `{'error': 'You cannot assign yourself as executor of your own task'}` with the status code `400 Bad Request`.
5. If the task already has an executor, return an error message `{'error': 'This task already has an executor'}` with the status code `400 Bad Request`.
6. If the task is available for assignment, set the current user as the executor and save the task.
8. Return a successful response with the status code `200 OK` and the message `{'message': 'You have been assigned as the executor of the task'}`.

### MarkTaskDoneAPIView

This view allows marking a task as done.

1. Only authenticated users can use this view.
2. The view implements the `patch` method, which receives the task identifier through the URL.
3. If the task is not found, it returns an error message `{'error': 'Task not found'}` with the status code `404 Not Found`.
4. If the current user is not the executor of the task, it returns an error message `{'error': 'You are not authorized to mark this task as done'}` with the status code `400 Bad Request`.
5. If all checks pass successfully, it sets the value of the `is_done` field to True for the current task and saves the changes.
6. It returns a successful response with the status code `200 OK`, passing the modified task data in JSON format as the response data.

Fields for the task: executor, name, cost, deadline.

### URLs

```python
urlpatterns = [
    path('app/user/create/', UserCreateView.as_view(), name='user_create'),
    path('app/login/', LoginView.as_view(), name='login'),
    path('app/logout/', LogoutView.as_view(), name='logout'),
    path('app/task/create/', TaskCreateView.as_view(), name='task_create'),
    path('app/tasks-created-by-user/', TasksCreatedByUser.as_view(), name='user_tasks'),
    path('app/user-tasks-stats/', UserTasksStatsAPIView.as_view(), name='user-tasks-stats'),
    path('app/unassigned-tasks/', UnassignedTasksAPIView.as_view(), name='unassigned-tasks'),
    path('app/task/executor/', TaskWithExecutorAPIView.as_view(), name='task_executor'),
    path('app/user-tasks/', UserTasksAPIView.as_view(), name='my-tasks'),
    path('app/become-executor/<int:task_id>/', BecomeExecutorAPIView.as_view(), name='become-executor'),
    path('app/mark-task-done/<int:task_id>/', MarkTaskDoneAPIView.as_view(), name='mark-task-done'),
    path('app/clear_db/', ClearDatabaseView.as_view(), name='clear_db'),
]
```

### ClearDatabaseView

This view clears the models for testing the API.

```python
class ClearDatabaseView(APIView):
    def post(self, request):
        Task.objects.all().delete()
        User.objects.all().delete()
        return Response({'message': 'All data cleared successfully'}, status=200)
```

This view is accessible at `app/clear_db/` and deletes all tasks and users from the database when accessed via a POST request.

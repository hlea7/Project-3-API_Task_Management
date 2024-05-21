# Task Management System

This Django application provides a comprehensive API for managing tasks. The functionalities include user creation, user authentication, task creation, and various views to interact with tasks and their statuses.

## Models

### Task

A model representing a task with the following fields:

- **creator**: ForeignKey to the built-in User model. Required.
- **executor**: ForeignKey to the built-in User model. Optional.
- **name**: CharField with a maximum length of 255 characters.
- **cost**: DecimalField with a maximum of 8 digits and 2 decimal places.
- **is_done**: BooleanField indicating task completion status.
- **deadline**: DateTimeField for the task's deadline.

## Views

### UserCreateView

Allows the creation of a user.

- **POST**: Creates a new user.
  - Requires `username`, `password`, and `email`.
  - Validates the presence of required fields.
  - Checks if the username already exists.
  - Returns user data on successful creation.

### LoginView

Allows user authentication and token retrieval.

- **POST**: Authenticates the user and returns an authentication token.
  - Requires `username` and `password`.
  - Returns an error if authentication fails.

### LogoutView

Allows an authenticated user to log out.

- **POST**: Deletes the user's authentication token.
  - Requires authentication.

### TaskCreateView

Allows the creation of a new task.

- **POST**: Creates a new task.
  - Requires `executor`, `name`, `cost`, and `deadline`.
  - Sets the creator as the current authenticated user.
  - Validates the creator is not the executor.
  - Checks if the specified executor exists.

### TasksCreatedByUser

Displays tasks created by the current user.

- **GET**: Returns a list of tasks created by the authenticated user.
  - Requires authentication.

### TaskWithExecutorAPIView

Displays all existing tasks.

- **GET**: Returns a list of all tasks, marking undefined executors as "undefined".

### UserTasksAPIView

Displays tasks assigned to the current user.

- **GET**: Returns a list of tasks where the current user is the executor.
  - Requires authentication.

### UserTasksStatsAPIView

Displays statistics for the tasks of the current user.

- **GET**: Returns statistics including completed tasks, pending tasks, overdue tasks, assigned tasks, total earned, and total spent.
  - Requires authentication.

### UnassignedTasksAPIView

Displays all tasks without an assigned executor.

- **GET**: Returns a list of tasks without an executor, sorted by cost.
  - Requires authentication.

### BecomeExecutorAPIView

Allows a user to become the executor of a task.

- **PATCH**: Assigns the current user as the executor of a specified task.
  - Requires task identifier through URL.
  - Validates the task's existence and current executor status.
  - Requires authentication.

### MarkTaskDoneAPIView

Allows marking a task as done.

- **PATCH**: Marks the specified task as done.
  - Requires task identifier through URL.
  - Validates task's existence and executor status.
  - Requires authentication.

### ClearDatabaseView

Clears all data from the models. Useful for testing.

- **POST**: Deletes all Task and User entries.
  - Returns a success message.

## URLS

The URLs for the application are prefixed with `app/`.

```plaintext
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
```

## Usage

Run the Django development server and navigate to the endpoints to interact with the task management system.

### Example URLs

- User creation: `http://127.0.0.1:8000/app/user/create/`
- User login: `http://127.0.0.1:8000/app/login/`
- Task creation: `http://127.0.0.1:8000/app/task/create/`

Ensure you are authenticated to access protected endpoints.
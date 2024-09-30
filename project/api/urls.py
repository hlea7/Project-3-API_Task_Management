from django.urls import path
from .views import *

urlpatterns = [
    path('user/create/', UserCreateView.as_view(), name='user_create'),
    path('clear_db/', ClearDatabaseView.as_view(), name='clear_db'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('task/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks-created-by-user/', TasksCreatedByUser.as_view(), name='user_tasks'),
    path('task/executor/', TaskWithExecutorAPIView.as_view(), name='task_executor'),
]
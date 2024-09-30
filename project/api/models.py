from django.db import models
from django.contrib.auth.models import User

# Task model stores info about the Task
class Task(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')
    executor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks_assigned')
    name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=8, decimal_places=2)
    is_done = models.BooleanField(default=False)
    deadline = models.DateField()

    def __str__(self):
        return f'{self.is_done} - {self.executor} - {self.deadline} - {self.name}'



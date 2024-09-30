from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    deadline = serializers.DateField(required=True)

    class Meta:
        model = Task
        fields = ['id', 'creator', 'executor', 'name', 'cost', 'deadline']
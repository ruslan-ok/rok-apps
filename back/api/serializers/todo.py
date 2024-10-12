from rest_framework import serializers
from task.models import Task

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'event', 'start', 'stop', 'completed', 'completion', 'in_my_day', 'important', 'remind',
            'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories', 'info', 'created', 'last_mod', 'groups',]


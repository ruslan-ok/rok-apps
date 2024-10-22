from rest_framework import serializers
from task.models import Task, Step

class TodoListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['url', 'id', 'name', 'event', 'start', 'stop', 'completed', 'completion', 'in_my_day', 'important', 'remind',
            'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories', 'info', 'created', 'last_mod',]

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'name', 'completed']

class TodoDetailsSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    class Meta:
        model = Task
        fields = ['url', 'id', 'name', 'event', 'start', 'stop', 'completed', 'completion', 'in_my_day', 'important', 'remind',
            'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories', 'info', 'created', 'last_mod', 'steps']


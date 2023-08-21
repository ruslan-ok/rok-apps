from rest_framework import serializers
from task.models import Task

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    task_1 = serializers.ReadOnlyField(source='task_1.name')
    task_2 = serializers.ReadOnlyField(source='task_2.name')
    task_3 = serializers.ReadOnlyField(source='task_3.name')
    class Meta:
        model = Task
        fields = ['url', 'user', 'name', 'event', 'start', 'stop', 'completed', 'completion', 'in_my_day', 'important', 
                'remind', 'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories', 'info',
                'src_id', 'created', 'last_mod', 'task_1', 'task_2', 'task_3', 'groups', 'active', 
                'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen', 
                'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo']


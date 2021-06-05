from rest_framework import serializers
from task.models import Group, Task

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    node_id = serializers.ReadOnlyField(source='node.id')
    app = serializers.ReadOnlyField()
    class Meta:
        model = Group
        fields = ['url', 'id', 'node', 'node_id', 'user', 'app', 'name', 'sort', 'is_open', 'is_leaf', 'level', 'qty']

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Task
        fields = ['url', 'user', 'name', 'created', 'in_my_day', 'important', 'completed', 'completion', 
                  'start', 'stop', 'remind', 'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories',
                  'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen', 
                  'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo']




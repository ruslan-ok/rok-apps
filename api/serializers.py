from rest_framework import serializers
from task.models import Group, Task, Step, Urls
from account.models import UserExt
from logs.models import ServiceEvent

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    node_id = serializers.ReadOnlyField(source='node.id')
    class Meta:
        model = Group
        fields = ['url', 'id', 'node', 'node_id', 'user', 'app', 'role', 'name', 'sort', 'created', 'last_mod',
                'completed', 'theme', 'sub_groups', 'determinator', 'view_id']
    def get_fields(self):
        fields = super().get_fields()
        request = self.context['request']
        fields['node'].queryset = Group.objects.filter(user=request.user.id)
        return fields

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
                'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo', 'item_attr']

class StepSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    task = serializers.ReadOnlyField(source='task.name')
    class Meta:
        model = Step
        fields = ['url', 'id', 'user', 'task', 'name', 'sort', 'completed']

class UrlsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Urls
        fields = ['url', 'id', 'task', 'num', 'href', 'status', 'hostname', 'title', 'created', 'last_mod']

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserExt
        fields = ['user', 'avatar', 'avatar_mini']

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceEvent
        fields = ['device', 'app', 'service', 'created', 'type', 'name', 'info']


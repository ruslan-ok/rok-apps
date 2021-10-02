from rest_framework import serializers
from task.models import Group, Task, Step, Urls
from account.models import UserExt
from apart.models import Apart, Meter, Service, Bill

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    node_id = serializers.ReadOnlyField(source='node.id')
    class Meta:
        model = Group
        fields = ['url', 'id', 'node', 'node_id', 'user', 'app', 'role', 'name', 'sort', 'created', 'last_mod']

class TaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Task
        fields = ['url', 'user', 'name', 'created', 'in_my_day', 'important', 'completed', 'completion', 
                'start', 'stop', 'remind', 'last_remind', 'repeat', 'repeat_num', 'repeat_days', 'categories',
                'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen', 
                'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo', 'item_attr']

class StepSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
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

class ApartSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Apart
        fields = ['url', 'user', 'name', 'addr', 'active', 'has_el', 'has_hw', 'has_cw', 'has_gas', 'has_ppo', 'info', 'task']

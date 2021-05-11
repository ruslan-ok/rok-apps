from django.db import models
from rest_framework import serializers
from .models import TaskGrp, ATask

class TaskGrpSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    app = serializers.ReadOnlyField()
    class Meta:
        model = TaskGrp
        fields = ['url', 'id', 'user', 'app', 'node', 'name', 'sort', 'is_open', 'is_leaf']

class TaskGrpSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskGrp
        fields = ['id', 'node', 'app', 'name', 'is_open']
    
class ATaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = ATask
        fields = ['url', 'user', 'grp', 'created', 'name', 'start', 'completed', 'completion', 'in_my_day', 'important', 'remind', 
                  'repeat', 'repeat_num', 'repeat_days', 'categories', 'info',
                  'app_task', 'app_note', 'app_news', 'app_store', 'app_doc', 'app_warr', 'app_expen', 
                  'app_trip', 'app_fuel', 'app_apart', 'app_health', 'app_work', 'app_photo']


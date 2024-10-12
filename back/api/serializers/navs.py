from rest_framework import serializers
from task.models import Task

class NavsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['url', 'name',]


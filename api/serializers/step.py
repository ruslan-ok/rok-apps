from rest_framework import serializers
from task.models import Step

class StepSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    task = serializers.ReadOnlyField(source='task.name')
    class Meta:
        model = Step
        fields = ['url', 'id', 'user', 'task', 'name', 'sort', 'completed']


from rest_framework import serializers
from task.models import Task

class WeightSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = ['url', 'id', 'name', 'event', 'bio_weight',]

from rest_framework import serializers
from task.models import VisitedHistory

class VisitedDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedHistory
        fields = ['id', 'pinned']


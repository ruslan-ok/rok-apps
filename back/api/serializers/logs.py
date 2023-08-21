from rest_framework import serializers
from logs.models import ServiceEvent

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceEvent
        fields = ['device', 'app', 'service', 'created', 'type', 'name', 'info']


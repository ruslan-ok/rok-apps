from rest_framework import serializers
from task.models import VisitedHistory

class VisitedHistorySerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = VisitedHistory
        fields = ['id', 'user', 'app', 'page', 'href', 'stamp', 'info', 'icon', 'pinned'
        ]

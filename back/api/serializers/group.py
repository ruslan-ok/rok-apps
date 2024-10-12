from rest_framework import serializers
from task.models import Group

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'node_id', 'name', 'act_items_qty']

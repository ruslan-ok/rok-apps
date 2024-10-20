from rest_framework import serializers
from task.models import Group

class ViewGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'app', 'role', 'theme', 'use_sub_groups', 'act_items_qty', 'sub_groups', 'use_sub_groups',
                  'determinator', 'view_id', 'items_sort']

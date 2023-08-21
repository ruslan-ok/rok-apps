from rest_framework import serializers
from task.models import Group

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    node_id = serializers.ReadOnlyField(source='node.id')
    class Meta:
        model = Group
        fields = ['url', 'id', 'node', 'node_id', 'user', 'app', 'role', 'name', 'sort', 'created', 'last_mod',
                'completed', 'theme', 'sub_groups', 'determinator', 'view_id']
    def get_fields(self):
        fields = super().get_fields()
        request = self.context['request']
        fields['node'].queryset = Group.objects.filter(user=request.user.id)
        return fields


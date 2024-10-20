from rest_framework import serializers
from api.serializers.view_group import ViewGroupSerializer

class PageConfigSerializer(serializers.Serializer):
    title = serializers.CharField()
    icon = serializers.CharField()
    event_in_name = serializers.BooleanField()
    use_selector = serializers.BooleanField()
    use_star = serializers.BooleanField()
    add_item = serializers.JSONField()
    related_roles = serializers.JSONField()
    possible_related = serializers.JSONField()
    entity = serializers.JSONField()
    sorts = serializers.JSONField()
    themes = serializers.JSONField()
    view_group = serializers.JSONField() # ViewGroupSerializer(many=False, read_only=False)

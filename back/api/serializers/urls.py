from rest_framework import serializers
from task.models import Urls

class UrlsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Urls
        fields = ['url', 'id', 'task', 'num', 'href', 'status', 'hostname', 'title', 'created', 'last_mod']

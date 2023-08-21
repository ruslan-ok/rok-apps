from rest_framework import serializers

class PageData(object):
    def __init__(self, json_data):
        self.json_data = json_data

class PageDataSerializer(serializers.Serializer):
    json_data = serializers.JSONField()

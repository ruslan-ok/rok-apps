from rest_framework import serializers
from account.models import UserExt

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = UserExt
        fields = ['user', 'avatar', 'avatar_mini']


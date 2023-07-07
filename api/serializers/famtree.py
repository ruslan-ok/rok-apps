from rest_framework import serializers
from family.models import FamTree

class FamTreeSerializer(serializers.HyperlinkedModelSerializer):
    # url = url = serializers.HyperlinkedIdentityField(view_name='family:pedigree-detail')
    class Meta:
        model = FamTree
        fields = ['url', 'id', 'name']

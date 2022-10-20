from rest_framework import serializers
from family.models import FamTree

from family.models import FamTree
class FamTreeSerializer(serializers.HyperlinkedModelSerializer):
    # url = url = serializers.HyperlinkedIdentityField(view_name='family:famtree-details')
    class Meta:
        model = FamTree
        fields = ['url', 'id', 'name']

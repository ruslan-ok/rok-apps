from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from task.models import Task
from serializers.navs import NavsSerializer

class NavsViewSet(ViewSet):

    def list(self, request):
        queryset = self.get_queryset(request)
        serializer = NavsSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = Task.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = NavsSerializer(user)
        return Response(serializer.data)

    def get_queryset(self, request):
        return None

from rest_framework import viewsets, permissions, renderers, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from task.models import Step
from api.serializers import StepSerializer
from todo.get_info import get_info as todo_get_info
from task.const import *

class StepViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return Step.objects.filter(user=self.request.user.id).order_by('-created')

    def perform_create(self, serializer):
        if 'sort' in self.request.POST:
            sort = self.request.POST['sort']
        else:
            task = self.request.POST['task'].split('/')
            task_id = task[-2]
            sort = Step.next_sort(task_id)
        serializer.save(user=self.request.user, sort=sort)

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()
        task.set_item_attr(APP_TODO, todo_get_info(task))
    
    @action(detail=True)
    def complete(self, request, pk=None):
        step = self.get_object()
        step.completed = not step.completed
        step.save()
        step.task.set_item_attr(APP_TODO, todo_get_info(step.task))
        serializer = StepSerializer(instance=step, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def rename(self, request, pk=None):
        if 'value' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'value'"},
                            status=status.HTTP_400_BAD_REQUEST)
        step = self.get_object()
        step.name = self.request.query_params['value']
        step.save()
        serializer = StepSerializer(instance=step, context={'request': request})
        return Response(serializer.data)
    
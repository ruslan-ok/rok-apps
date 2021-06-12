from rest_framework import viewsets, permissions, renderers, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from task.models import Step, Task
from api.serializers import StepSerializer

class StepViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return Step.objects.filter(user=self.request.user).order_by('-created')

    def perform_create(self, serializer):
        if 'sort' in self.request.POST:
            sort = self.request.POST['sort']
        else:
            task = self.request.POST['task'].split('/')
            task_id = task[-2]
            sort = Step.next_sort(task_id)
        serializer.save(user=self.request.user, sort=sort)
    
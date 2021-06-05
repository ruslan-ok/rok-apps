import math
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from task.models import Group, Task, TaskGroup
from rusel.apps import APPS
from api.serializers import GroupSerializer
from api.converter import convert
from rusel.apps import switch_beta

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        if 'app' in self.request.query_params:
            app = self.request.query_params['app']
            return Group.objects.filter(user=self.request.user, app=app).order_by('-created')
        return Group.objects.filter(user=self.request.user).order_by('-created')
    
    @action(detail=False)
    def get_qty(self, request, pk=None):
        qty = len(self.get_queryset())
        return Response({'qty': qty})
    
    @action(detail=True)
    def get_list(self, request, pk=None):
        return HttpResponseRedirect(reverse('taskgrp-list'))
    
    @action(detail=True)
    def toggle(self, request, pk=None):
        grp = self.get_object()
        grp.is_open = not grp.is_open
        grp.save()
        serializer = GroupSerializer(instance=grp, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def get_tasks(self, request, pk=None):
        return Response('')

    @action(detail=False)
    def sort(self, request, pk=None):
        if 'app' not in self.request.query_params:
            for app in APPS:
                self.sort_level(self.request.user, app, None, '', 0)
        else:
            app = self.request.query_params['app']
            if app not in APPS:
                return Response({'Error': "The 'app' parameter must have one of the following values: " + ', '.join(APPS)},
                                status=status.HTTP_400_BAD_REQUEST)
            self.sort_level(self.request.user, app, None, '', 0)

        serializer = GroupSerializer(context={'request': request}, many=True)
        return Response(serializer.data)
    
    def sort_level(self, user, app, node, parent_code, level):
        num = 1
        groups = Group.objects.filter(user=user.id, app=app, node=node).order_by('name')
        code_len = math.ceil(math.log10(len(groups)+1))
        for grp in groups:
            grp.sort = parent_code + str(num).zfill(code_len)
            grp.level = level
            grp.is_leaf = (len(Group.objects.filter(user=user.id, app=app, node=grp.id)) == 0)
            if grp.is_leaf:
                grp.qty = len(TaskGroup.objects.filter(group=grp.id))
            else:
                grp.qty = 0
            grp.save()
            num += 1
            self.sort_level(user, app, grp.id, grp.sort, level+1)

    @action(detail=False)
    def move(self, request, pk=None):
        result = convert()
        for app in APPS:
            self.sort_level(self.request.user, app, None, '', 0)
        switch_beta(request.user)
        return Response(result)

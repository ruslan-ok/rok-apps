import math
import urllib.parse
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from task.models import Group, Task, TaskGroup
from task.const import ALL_ROLES
from rusel.apps import APPS
from api.serializers import GroupSerializer
from api.converter_v3 import convert_v3

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.validated_data['name'] = urllib.parse.unquote(serializer.initial_data['name'])
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if not Group.objects.filter(node=instance.id).exists():
            if not TaskGroup.objects.filter(group=instance.id).exists():
                instance.delete()

    def get_queryset(self):
        if 'role' in self.request.query_params:
            role = self.request.query_params['role']
            return Group.objects.filter(user=self.request.user, role=role).order_by('-created')
        return Group.objects.filter(user=self.request.user).order_by('-created')
    
    @action(detail=False)
    def get_qty(self, request, pk=None):
        qty = len(self.get_queryset())
        return Response({'qty': qty})
    
    @action(detail=True)
    def get_list(self, request, pk=None):
        return HttpResponseRedirect(reverse('taskgrp-list'))
    
    @action(detail=True)
    def get_tasks(self, request, pk=None):
        return Response('')

    @action(detail=True)
    def toggle_sub_group(self, request, pk=None):
        if 'sub_group_id' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'sub_group_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        sub_group_id = self.request.query_params['sub_group_id']
        group = self.get_object()
        group.toggle_sub_group(sub_group_id)
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def set_theme(self, request, pk=None):
        if 'theme_id' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'theme_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        theme_id = self.request.query_params['theme_id']
        group = self.get_object()
        group.set_theme(theme_id)
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False)
    def sort(self, request, pk=None):
        if 'role' not in self.request.query_params:
            for role in ALL_ROLES:
                self.sort_level(self.request.user, role, None, '', 0)
        else:
            role = self.request.query_params['role']
            if role not in ALL_ROLES:
                return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(ALL_ROLES)},
                                status=status.HTTP_400_BAD_REQUEST)
            self.sort_level(self.request.user, role, None, '', 0)

        serializer = GroupSerializer(context={'request': request}, many=True)
        return Response(serializer.data)
    
    def sort_level(self, user, role, node, parent_code, level):
        num = 1
        groups = Group.objects.filter(user=user.id, role=role, node=node).order_by('name')
        code_len = math.ceil(math.log10(len(groups)+1))
        for grp in groups:
            grp.sort = parent_code + str(num).zfill(code_len)
            grp.level = level
            grp.is_leaf = (len(Group.objects.filter(user=user.id, role=role, node=grp.id)) == 0)
            if grp.is_leaf:
                grp.qty = len(TaskGroup.objects.filter(group=grp.id))
            else:
                grp.qty = 0
            grp.save()
            num += 1
            self.sort_level(user, role, grp.id, grp.sort, level+1)

    @action(detail=False)
    def convert_v2_to_v3(self, request, pk=None):
        result = convert_v3()
        for app in APPS:
            self.sort_level(self.request.user, app, None, '', 0)
        return Response(result)
    

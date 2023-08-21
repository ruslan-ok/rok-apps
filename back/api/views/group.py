from datetime import datetime
import math, os
import urllib.parse
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from task.models import Group, TaskGroup
from task.const import ALL_ROLES
from api.serializers.group import GroupSerializer

class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.validated_data['name'] = urllib.parse.unquote(serializer.initial_data['name'])
        serializer.validated_data['act_items_qty'] = 0
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
    
    @action(detail=True)
    def set_sort(self, request, pk=None):
        if 'sort_id' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'sort_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        sort_id = self.request.query_params['sort_id']
        group = self.get_object()
        group.set_sort(sort_id)
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def reverse_sort(self, request, pk=None):
        group = self.get_object()
        group.reverse_sort()
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def delete_sort(self, request, pk=None):
        group = self.get_object()
        group.delete_sort()
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

    @action(detail=True)
    def toggle_sub_groups(self, request, pk=None):
        group = self.get_object()
        group.use_sub_groups = not group.use_sub_groups
        group.save()
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)

    @action(detail=True)
    def toggle_services_visible(self, request, pk=None):
        group = self.get_object()
        group.services_visible = not group.services_visible
        group.save()
        serializer = GroupSerializer(instance=group, context={'request': request})
        return Response(serializer.data)

    @action(detail=False)
    def create_folder(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'name' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'name'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = 'docs'
        if 'app' in self.request.query_params:
            app = self.request.query_params['app']
        app += '/'
        folder = self.request.query_params['folder']
        name = self.request.query_params['name']
        storage_path = os.environ.get('DJANGO_STORAGE_PATH')
        store_dir = storage_path.format(request.user.username) + app + '/'
        try:
            os.mkdir(store_dir + folder + '/' + name)
            return Response({'result': 'ok'})
        except Exception as ex:
            ret = {'result': 'exception', 'exception': ex.strerror}
            return Response(ret)

    @action(detail=False)
    def rename_folder(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'new_name' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'new_name'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = 'docs'
        if 'app' in self.request.query_params:
            app = self.request.query_params['app']
        app += '/'
        path = ''
        if 'path' in self.request.query_params:
            path = self.request.query_params['path']
        folder = self.request.query_params['folder']
        new_name = self.request.query_params['new_name']
        storage_path = os.environ.get('DJANGO_STORAGE_PATH')
        store_dir = storage_path.format(request.user.username) + app + '/'
        old_path = store_dir + path + folder
        new_path = store_dir + path + new_name
        try:
            os.rename(old_path, new_path)
            return Response({'result': 'ok'})
        except Exception as ex:
            ret = {'result': 'exception', 'exception': ex.strerror}
            return Response(ret)

    @action(detail=False)
    def delete_folder(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = 'docs'
        if 'app' in self.request.query_params:
            app = self.request.query_params['app']
        app += '/'
        path = ''
        if 'path' in self.request.query_params:
            path = self.request.query_params['path']
        folder = self.request.query_params['folder']
        storage_path = os.environ.get('DJANGO_STORAGE_PATH')
        store_dir = storage_path.format(request.user.username) + app + '/'
        folder_path = store_dir + path + folder
        try:
            os.rmdir(folder_path)
            return Response({'result': 'ok'})
        except Exception as ex:
            ret = {'result': 'exception', 'exception': ex.strerror}
            return Response(ret)

    # Modify the modification time of a file.
    @action(detail=False)
    def ftp_mfmt(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'file' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'file'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'mod_time' not in self.request.query_params:
            return Response({'result': 'error', 'error': "Expected parameter 'mod_time'"},
                            status=status.HTTP_400_BAD_REQUEST)
        folder = self.request.query_params['folder']
        file = self.request.query_params['file']
        mod_time_str = self.request.query_params['mod_time']
        mod_time = datetime.strptime(mod_time_str, '%m-%d-%Y %I:%M%p')
        dt_epoch = mod_time.timestamp()
        try:
            work_dir = os.environ.get('DJANGO_BACKUP_FOLDER')
            path = os.path.join(work_dir, folder)
            fname = os.path.join(path, file)
            os.utime(fname, (dt_epoch, dt_epoch))
            return Response({'result': 'ok'})
        except Exception as ex:
            ret = {'result': 'exception', 'exception': ex.strerror}
            return Response(ret)

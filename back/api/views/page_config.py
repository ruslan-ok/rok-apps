from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, permissions, renderers
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers.view_group import ViewGroupSerializer
from api.serializers.page_config import PageConfigSerializer
from task.models import Group
from task.const import APP_TODO
from core.context import Context, get_group_path


BG_IMAGES = [
    'beach',
    'desert',
    'fern',
    'field',
    'gradient',
    'lighthouse',
    'safari',
    'sea',
    'tv_tower'
]

class PageConfigView(APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PageConfigSerializer
    renderer_classes = [renderers.JSONRenderer]

    def get(self, request):
        context = Context()
        context.request = request
        context.set_config(APP_TODO)
        config = context.config
        config.set_view(request)

        related_roles = []
        possible_related = []

        group_path = []
        group_id = request.query_params.get('group')
        if group_id:
            group_id = int(group_id)
            group = Group.objects.filter(id=group_id).get()
            if (not group.determinator) or (group.determinator == 'group'):
                group_path = get_group_path(group_id)

        if config.view_sorts:
            sorts = config.view_sorts
        else:
            sorts = config.app_sorts
        sorts = [{'id': x[0], 'name': x[1].capitalize()} for x in sorts] if sorts else []

        themes = []
        for x in range(24):
            if (x < 14) or (x == 23):
                themes.append({'id': x+1, 'style': 'theme-' + str(x+1)})
            else:
                themes.append({'id': x+1, 'style': 'theme-' + str(x+1), 'img': BG_IMAGES[x-14]})

        view_group_serializer = ViewGroupSerializer(config.cur_view_group, many=False)
        view_group = view_group_serializer.data

        data = {
            'title': config.title.capitalize(),
            'icon': config.view_icon,
            'event_in_name': config.event_in_name,
            'use_selector': config.use_selector,
            'use_star': config.use_important,
            'add_item': {
                'type': 'input',
                'placeholder': 'Add todo',
            },
            'related_roles': related_roles,
            'possible_related': possible_related,
            'entity': {
                'name': 'group',
                'id': group_id,
                'path': group_path,
            },
            'sorts': sorts,
            'themes': themes,
            'theme_id': 8,
            'view_group': view_group,
        }
        serializer = PageConfigSerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data)
        print(serializer.errors)
        return Response({})
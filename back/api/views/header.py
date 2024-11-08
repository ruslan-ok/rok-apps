from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from core.applications import get_apps_list


def get_header_data(user: User | None, local: bool, version):
    data = {
        'appIcon': '/static/rok.png',
        'appTitle': '',
        'applications': [],
        'searchText': '',
        'userName': None,
        'avatar': None,
        'userMenu': [],
        'buttons': [],
    }
    if not user or not user.is_authenticated:
        data['appTitle'] = settings.DOMAIN_NAME
        data['buttons'].append({'button_id': 'demo', 'name': 'Demo', 'href': '/demo'})
        data['buttons'].append({'button_id': 'login', 'name': 'Log in', 'href': '/login'})
    else:
        data['applications'] = get_apps_list(user, 'core')
        data['searchPlaceholder'] = 'Search...'
        data['userName'] = user.username if user else None
        if user and hasattr(user, 'userext') and user.userext.avatar_mini:
            data['avatar'] = user.userext.avatar_mini.url
        else:
            data['avatar'] = '/static/Default-avatar.jpg'
        if user and user.username != 'demouser':
            data['userMenu'].append({'item_id': 'profile', 'name': 'Profile', 'href': '/profile', 'icon': 'bi-person'})
            data['userMenu'].append({'item_id': 'separator', 'name': '', 'href': '', 'icon': ''})
        data['userMenu'].append({'item_id': 'logout', 'name': 'Log out', 'href': '/logout', 'icon': 'bi-box-arrow-right'})
    return data

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def header(request):
    local = 'localhost' in request.get_host()
    version = request.query_params.get('version')
    data = get_header_data(request.user, local, version)
    return Response(data)


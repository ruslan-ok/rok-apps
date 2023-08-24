import os, json
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group
from django.http import FileResponse, HttpResponseNotFound

from react.api.serializers import PageData, PageDataSerializer
from account.models import UserExt
from account.views import generate_activation_key
from core.applications import get_apps_list
from rusel.views import get_hp_widgets
from rusel.settings import ENV

def get_assets(request, file):
    try:
        static_path = os.environ.get('DJANGO_STATIC_ROOT' + ENV, '')
        folder = os.path.join(static_path, 'assets')
        filepath = folder + '\\' + file
        fsock = open(filepath, 'rb')
        response = FileResponse(fsock)
        return response
    except IOError:
        return HttpResponseNotFound()


def get_header_data(is_authorised: bool, user: User | None):
    data = {
        'appIcon': '/static/rusel.png',
        'appTitle': '',
        'applications': [],
        'searchText': '',
        'userName': None,
        'avatar': None,
        'userMenu': [],
        'buttons': [],
    }
    if not is_authorised:
        data['appTitle'] = 'rusel.by'
        data['buttons'].append({'button_id': 'demo', 'name': 'Demo', 'href': 'demo'})
        data['buttons'].append({'button_id': 'login', 'name': 'Log in', 'href': 'login'})
    else:
        data['applications'] = get_apps_list(user, 'home')
        data['searchPlaceholder'] = 'Search...'
        data['userName'] = user.username if user else None
        if hasattr(user, 'userext') and user.userext.avatar_mini:
            data['avatar'] = user.userext.avatar_mini.url
        else:
            data['avatar'] = '/static/Default-avatar.jpg'
        if user and user.username != 'demouser':
            data['userMenu'].append({'item_id': 'profile', 'name': 'Profile', 'href': 'profile', 'icon': 'bi-person'})
            data['userMenu'].append({'item_id': 'separator', 'name': '', 'href': '', 'icon': ''})
        data['userMenu'].append({'item_id': 'logout', 'name': 'Sign out', 'href': 'logout', 'icon': 'bi-box-arrow-right'})
    return data

def get_public_data(is_authorised: bool):
    if is_authorised:
        return {'applications': [] }
    data = [
        {
            'app_id': 'Tasks',
            'icon': 'check2-square',
            'title': 'Capabilities:',
            'features': [
                'Combining tasks into lists, and lists into groups.',
                'Search by name, task description and task categories.',
                'Reminder of tasks by pop-up messages of the browser on the computer and in the phone.',
                'For each task, execution stages can be set, tracking of the execution of both the task itself and its stages is available.',
                'For a task, a due date, frequency of repetition, date and time of reminder can be set.',
                'A task can be marked as "important" or as added to the "My Day" view.',
                'Each task can be assigned an arbitrary number of "categories" and filter the list of tasks by them.',
                'In the task, you can specify a hyperlink to an external Internet resource.',
                'You can attach an arbitrary number of files to the task.',
            ],
        },
        {
            'app_id': 'Note',
            'icon': 'sticky',
            'title': 'Personal notes about everything. For each note, in addition to the description, you can specify a hyperlink to an external Internet resource, an arbitrary number of categories, attach files. Notes, like tasks, are combined into lists, and lists into groups. Notes can be searched by title, description, and category.',
            'features': [],
        },
        {
            'app_id': 'News',
            'icon': 'newspaper',
            'title': 'Similar to a list of notes, but the emphasis is on the date-time of publication.',
            'features': [],
        },
        {
            'app_id': 'Proj',
            'icon': 'piggy-bank',
            'title': 'Allows you to track costs for several projects. Multiple currencies can be selected for accounting and totals.',
            'features': [],
        },
        {
            'app_id': 'Fuel',
            'icon': 'droplet',
            'title': 'For the car owner the ability to control fuel consumption, as well as the frequency of service maintenance and replacement of consumable materials.',
            'features': [],
        }
    ]
    return {'applications': data }

def get_protected_data(is_authorised: bool, user: User):
    data = {
        'widgets': []
    }
    if is_authorised and user:
        data['widgets'] = get_hp_widgets(user)
    return data

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def header(request):
    token = request.GET.get('userToken', '')
    result = do_check_token(token)
    data = get_header_data(result['ok'], result['user'])
    json_data = json.dumps(data)
    obj = PageData(json_data=json_data)
    serializer = PageDataSerializer(obj)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def main_page(request):
    token = request.GET.get('userToken', '')
    result = do_check_token(token)
    data = {
        'publicData': get_public_data(result['ok']),
        'protectedData': get_protected_data(result['ok'], result['user']),
    }
    json_data = json.dumps(data)
    obj = PageData(json_data=json_data)
    serializer = PageDataSerializer(obj)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def demo(request):
    demouserpassword = os.environ.get('DJANGO_DEMOUSER_PWRD')
    if not User.objects.filter(username = 'demouser').exists():
        user = User.objects.create_user('demouser', 'demouser@rusel.by', demouserpassword)
        main_group = Group.objects.get(name='Users')
        user.groups.add(main_group)
    user = authenticate(username='demouser', password=demouserpassword)
    if user is not None:
        auth_login(request, user)
    return Response({"user": user.get_username() if user else None})

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def login(request):
    username = request.data['username']
    password = request.data['password']
    if not username or not password:
        return Response({ 'ok': False, 'info': 'The "username" and "password" fields must be filled in.', 'accessToken': None, 'expires': None })
    user = None
    if username and password:
        user = authenticate(request, username=username, password=password)
    if not user:
        return Response({ 'ok': False, 'info': 'Please enter a correct username and password. Note that both fields may be case-sensitive.', 'username': username, 'accessToken': None, 'expires': None })
    auth_login(request, user)
    ue = UserExt.objects.filter(user=user.id).get()
    ue.access_token = generate_activation_key(username=ue.user.username)
    ue.expires = datetime.now() + timedelta(30)
    ue.save()
    #print({ 'ok': True, 'username': user.get_username(), 'accessToken': ue.access_token, 'expires': 30 })
    return Response({ 'ok': True, 'username': user.get_username(), 'accessToken': ue.access_token, 'expires': 30 })

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def logout(request):
    auth_logout(request)
    return Response({ 'ok': True, 'username': '' })

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def check_token(request):
    token = request.data['accessToken']
    ret = do_check_token(token)
    return Response({ 'ok': ret['ok'], 'username': ret['username'], 'expires': ret['expires'] })

def do_check_token(token):
    if UserExt.objects.filter(access_token=token, expires__gt=datetime.now()).exists():
        ue = UserExt.objects.filter(access_token=token, expires__gt=datetime.now()).get()
        user = User.objects.filter(id=ue.user.id).get()
        if ue.expires:
            delta = (ue.expires - datetime.now()).days
            return { 'ok': True, 'username': user.username, 'expires': delta, 'user': user }
    return { 'ok': False, 'username': None, 'expires': None, 'user': None }

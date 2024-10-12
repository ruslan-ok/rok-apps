from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User, Group


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def auth(request):
    if request.user and request.user.is_authenticated:
        return Response({ 'ok': 'ok', 'username': request.user.username })
    return Response({ 'ok': 'ok', 'username': None })

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def demo(request):
    demouser_password = settings.DJANGO_DEMOUSER_PWRD
    demouser_email = settings.EMAIL_DEMOUSER
    if not User.objects.filter(username = 'demouser').exists():
        user = User.objects.create_user('demouser', demouser_email, demouser_password)
        main_group = Group.objects.get(name='Users')
        user.groups.add(main_group)
    user = authenticate(username='demouser', password=demouser_password)
    if user is None:
        return Response({ 'ok': False, 'info': 'User "demouser" not found.' })
    auth_login(request, user)
    if not user.is_authenticated:
        return Response({ 'ok': False, 'info': 'User "demouser" is not authenticated.' })
    return Response({ 'ok': True, 'info': user.get_username() })

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def login(request):
    username = request.data['username']
    password = request.data['password']
    if not username or not password:
        return Response({ 'ok': False, 'info': 'The "username" and "password" fields must be filled in.' })
    user = None
    if username and password:
        user = authenticate(request, username=username, password=password)
    if not user:
        return Response({ 'ok': False, 'info': 'Please enter a correct username and password. Note that both fields may be case-sensitive.' })
    auth_login(request, user)
    return Response({ 'ok': True, 'info': user.get_username() })

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def logout(request):
    auth_logout(request)
    return Response({ 'ok': True, 'username': '' })

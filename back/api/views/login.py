from django.conf import settings
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers.login import LoginSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_setup(request):
    return Response({ 'info': 'csrf' })

@method_decorator(csrf_protect, name="post")
class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    # @csrf_protect_method
    # @csrf_protect
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer:
            user = serializer.validated_data['user']
            login(request, user)
        return Response({ 'ok': True, 'info': user.get_username() })

from rest_framework import viewsets, permissions, renderers
from api.serializers.profile import ProfileSerializer
from account.models import UserExt
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response

class ProfileViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]

    def get_queryset(self):
        return UserExt.objects.filter(user=self.request.user.id)

    @action(detail=False)
    def delete_avatar(self, request, pk=None):
        userext = UserExt.objects.filter(user=request.user.id).get()
        userext.avatar = None
        userext.avatar_mini = None
        userext.save()
        serializer = ProfileSerializer(instance=userext, context={'request': request})
        return Response({})

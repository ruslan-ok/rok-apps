import urllib.parse
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.family import FamTreeSerializer
from family.gedcom_551.exp import ExpGedcom551
from family.gedcom_551.imp import ImpGedcom551
from family.models import FamTreeUser, IndividualRecord
from family.utils import update_media


class FamTreeViewSet(viewsets.ModelViewSet):
    serializer_class = FamTreeSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.validated_data['name'] = urllib.parse.unquote(serializer.initial_data['name'])
        super().perform_create(serializer)

    def perform_destroy(self, instance):
        if not IndividualRecord.objects.filter(tree=instance.id).exists():
            instance.delete()

    def get_queryset(self):
        return FamTreeUser.objects.filter(user_id=self.request.user.id)

    @action(detail=False)
    def import_gedcom_5_5_1(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        folder = self.request.query_params['folder']
        mgr = ImpGedcom551(request)
        res = mgr.import_gedcom_551(folder)
        return Response(res)

    @action(detail=False)
    def export_gedcom_5_5_1(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        folder = self.request.query_params['folder']
        mgr = ExpGedcom551(request)
        res = mgr.export_gedcom_551(folder)
        return Response(res)
    
    @action(detail=True)
    def update_media(self, request, pk=None):
        updated = update_media(pk)
        return Response({'updated': updated})
    
    @action(detail=True)
    def important(self, request, pk=None):
        user_tree = FamTreeUser.objects.filter(user_id=request.user.id, id=pk).get()
        if user_tree.tree_id:
            return Response({'result': 'ok', 'tree_id': user_tree.tree_id})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})

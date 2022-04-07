from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.genealogy import GenealogySerializer
from genea.gedcom_551.exp import ExpGedcom551
from genea.gedcom_551.imp import ImpGedcom551


class GenealogyViewSet(viewsets.ModelViewSet):
    serializer_class = GenealogySerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return []

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
    

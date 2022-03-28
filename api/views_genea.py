from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.genealogy import GenealogySerializer
from genea.exp_imp import GenExpImp


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
    def import_myheritage(self, request, pk=None):
        mgr = GenExpImp(request)
        res = mgr.import_from_myheritage()
        return Response(res)
    

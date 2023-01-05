import urllib.parse
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.family import FamTreeSerializer
from family.gedcom_551.exp import ExpGedcom551
from family.gedcom_551.imp import ImpGedcom551
from family.models import FamTreeUser, FamTree, Params, IndividualRecord, PersonalNameStructure, PersonalNamePieces, ChildToFamilyLink, FamRecord, IndividualEventStructure, EventDetail
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

    def get_queryset(self):
        ret = []
        ftu = FamTreeUser.objects.filter(user_id=self.request.user.id)
        for ft in ftu:
            if ft.tree_id:
                if FamTree.objects.filter(id=ft.tree_id).exists():
                    tree = FamTree.objects.filter(id=ft.tree_id).get()
                    ret.append(tree)
        return ret

    @action(detail=False)
    def import_gedcom_5_5_1(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        folder = self.request.query_params['folder']
        mgr = ImpGedcom551(request)
        res = mgr.import_gedcom_551(folder)
        return Response(res)

    @action(detail=True)
    def export_gedcom_5_5_1(self, request, pk=None):
        if 'folder' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'folder'"},
                            status=status.HTTP_400_BAD_REQUEST)
        folder = self.request.query_params['folder']
        mgr = ExpGedcom551(request)
        res = mgr.export_gedcom_551(folder, pk)
        return Response(res)
    
    @action(detail=True)
    def update_media(self, request, pk=None):
        updated = update_media(pk)
        return Response({'updated': updated})
    
    @action(detail=True)
    def set_active(self, request, pk=None):
        if FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk).exists():
            if FamTree.objects.filter(id=pk).exists():
                tree = FamTree.objects.filter(id=pk).get()
                Params.set_cur_tree(self.request.user, tree)
                return Response({'result': 'ok', 'tree_id': pk})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})

    @action(detail=True)
    def get_tree(self, request, pk):
        if FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk).exists():
            if FamTree.objects.filter(id=pk).exists():
                tree = FamTree.objects.filter(id=pk).get()
                mgr = ExpGedcom551(request)
                gedcom = mgr.export_gedcom_551_str(tree)
                return Response({'result': 'ok', 'tree': gedcom})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})


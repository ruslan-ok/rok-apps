from django.db.models import Subquery
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.family import FamTreeSerializer
from family.gedcom_551.exp import ExpGedcom551
from family.gedcom_551.imp import ImpGedcom551
from family.models import FamTreeUser, FamTree, Params, FamTreePermission
from family.utils import update_media


class FamTreeViewSet(viewsets.ModelViewSet):
    serializer_class = FamTreeSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def destroy(self, request, pk=None):
        can_delete = False
        tree = self.get_object()
        if FamTreePermission.objects.filter(user=request.user.id, tree=tree.id).exists():
            ftp = FamTreePermission.objects.filter(user=request.user.id, tree=tree.id).get()
            can_delete = ftp.can_delete
        if can_delete:
            tree.delete_gedcom_file(request.user)
            return super().destroy(request, pk)
        else:
             return Response(status=status.HTTP_403_FORBIDDEN)


    def get_queryset(self):
        ftu = FamTreeUser.objects.filter(user_id=self.request.user.id, can_view=True)
        ft = FamTree.objects.filter(id__in=Subquery(ftu.values('tree_id')))
        return ft

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
        mgr = ExpGedcom551(request.user)
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
                mgr = ExpGedcom551(request.user)
                gedcom = mgr.export_gedcom_551_str(tree)
                return Response({'result': 'ok', 'tree': gedcom})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})

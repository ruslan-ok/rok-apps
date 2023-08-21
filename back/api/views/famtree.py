from django.db.models import Subquery
from rest_framework import viewsets, permissions, status, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers.famtree import FamTreeSerializer
from family.gedcom_551.exp import ExpGedcom551
from family.gedcom_551.imp import ImpGedcom551
from family.models import FamTreeUser, FamTree, Params, FamTreePermission, Gedcom, IndividualRecord, UserSettings
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
        if not can_delete:
            return Response(status=status.HTTP_403_FORBIDDEN)
        tree.delete_gedcom_file(request.user)
        cur_tree = Params.get_cur_tree(request.user)
        change_active = cur_tree == tree
        ret = super().destroy(request, pk)
        if change_active and FamTreeUser.objects.filter(user_id=request.user.id).exists():
            ftu = FamTreeUser.objects.filter(user_id=request.user.id)[0]
            ftu.set_active(request.user)
        return ret

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
        mgr = ImpGedcom551(request.user)
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
            FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk).get().set_active(request.user)
            return Response({'result': 'ok', 'tree_id': pk})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})

    @action(detail=True)
    def get_tree(self, request, pk):
        if FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk).exists():
            gedcom = ''
            for row in Gedcom.objects.filter(tree=pk, used_by_chart=True).order_by('row_num'):
                gedcom += row.value + '\n'
            if gedcom:
                return Response({'result': 'ok', 'tree': gedcom})
            else:
                return Response({'result': 'error', 'info': 'GEDCOM data not generated.'})
        return Response({'result': 'error', 'info': 'Specified family tree not found.'})

    @action(detail=True)
    def make_gedcom(self, request, pk=None):
        mgr = ExpGedcom551(request.user)
        ret = mgr.make_gedcom(pk)
        return Response(ret)

    @action(detail=True)
    def set_sel_indi(self, request, pk=None):
        if not FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk).exists():
            return Response({'result': 'error', 'info': 'Specified family tree not found.'})
        if 'indi_id' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'indi_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        str_indi_id = self.request.query_params['indi_id']
        indi_id = int(str_indi_id.replace('@I', '').replace('@', ''))
        indi = IndividualRecord.objects.filter(id=indi_id).get()
        tree = FamTree.objects.filter(id=pk).get()
        UserSettings.set_sel_indi(request.user, tree, indi)
        return Response({'result': 'ok', 'tree_id': pk, 'indi_id': str_indi_id})

from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import CreateSourceForm
from family.models import FamTreeUser, SourceRecord

class SourceListView(GenealogyListView):
    model = SourceRecord
    form_class = CreateSourceForm
    template_name = 'family/source/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return SourceRecord.objects.filter(tree_id=tree_id)
        return []

class SourceDetailsView(GenealogyDetailsView):
    model = SourceRecord
    form_class = CreateSourceForm
    template_name = 'family/source/detail.html'

from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import CreateSubmitterForm
from family.models import FamTreeUser, SubmitterRecord

class SubmitterListView(GenealogyListView):
    model = SubmitterRecord
    form_class = CreateSubmitterForm
    template_name = 'family/submitter/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return SubmitterRecord.objects.filter(tree_id=tree_id)
        return []

class SubmitterDetailsView(GenealogyDetailsView):
    model = SubmitterRecord
    form_class = CreateSubmitterForm
    template_name = 'family/submitter/detail.html'

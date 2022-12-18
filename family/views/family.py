from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import (CreateFamForm, )
from family.models import (FamTreeUser, FamRecord, )

class FamListView(GenealogyListView):
    model = FamRecord
    form_class = CreateFamForm
    template_name = 'family/family/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return FamRecord.objects.filter(tree=tree_id)
        return []

class FamDetailsView(GenealogyDetailsView):
    model = FamRecord
    form_class = CreateFamForm
    template_name = 'family/family/detail.html'

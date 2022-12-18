from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import CreateRepoForm
from family.models import FamTreeUser, RepositoryRecord

class RepoListView(GenealogyListView):
    model = RepositoryRecord
    form_class = CreateRepoForm
    template_name = 'family/repo/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return RepositoryRecord.objects.filter(tree_id=tree_id)
        return []

class RepoDetailsView(GenealogyDetailsView):
    model = RepositoryRecord
    form_class = CreateRepoForm
    template_name = 'family/repo/detail.html'

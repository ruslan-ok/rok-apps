from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import CreateMediaForm
from family.models import FamTreeUser, MultimediaRecord

class MediaListView(GenealogyListView):
    model = MultimediaRecord
    form_class = CreateMediaForm
    template_name = 'family/media/list.html'

    def get_queryset(self):
        if 'ft' in self.kwargs:
            tree_id = int(self.kwargs['ft'])
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return MultimediaRecord.objects.filter(tree_id=tree_id)
        return []

class MediaDetailsView(GenealogyDetailsView):
    model = MultimediaRecord
    form_class = CreateMediaForm
    template_name = 'family/media/detail.html'

from dataclasses import dataclass
from django.urls import reverse
from django.shortcuts import get_object_or_404
from family.views.base import GenealogyListView, GenealogyDetailsView
from family.forms import CreateFamTreeForm, EditFamTreeForm
from family.models import FamTree, FamTreeUser, Params, IndividualRecord, FamRecord

@dataclass
class Pedigree:
    id: int
    name: str
    important: bool
    mod_date: str
    num_indi: int
    num_fam: int

    def get_absolute_url(self):
        return reverse('family:pedigree-detail', args=(self.id,))

    def get_custom_attr(self):
        return [{'text': self.mod_date}, {'text': f'{self.num_indi} Individuals'}, {'text': f'{self.num_fam} Families'}]


class PedigreeListView(GenealogyListView):
    model = FamTreeUser
    form_class = CreateFamTreeForm
    template_name = 'family/pedigree/list.html'

    def get_queryset(self):
        ft = FamTreeUser.objects.filter(user_id=self.request.user.id)
        user_tree = Params.get_cur_tree(self.request.user)
        ret = []
        for t in ft:
            if t.name:
                important = False
                if user_tree:
                    important = t.tree_id == int(user_tree.id)
                num_indi = len(IndividualRecord.objects.filter(tree=t.tree_id))
                num_fam = len(FamRecord.objects.filter(tree=t.tree_id))
                ret.append(Pedigree(id=t.tree_id, name=t.name, important=important, mod_date=t.last_mod.strftime('%d.%m.%Y'), num_indi=num_indi, num_fam=num_fam))
        return ret

class PedigreeDetailsView(GenealogyDetailsView):
    model = FamTree
    form_class = EditFamTreeForm
    template_name = 'family/pedigree/detail.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['sour_corp_addr'] = 'todo::sour_corp_addr'
        context['tree_id'] = self.get_object().id
        return context

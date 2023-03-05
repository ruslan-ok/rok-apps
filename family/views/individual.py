from typing import List
from dataclasses import asdict
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from family.views.base import GenealogyDetailsView
from family.forms import EditIndividualForm
from family.models import IndividualRecord
from family.views.life_data import LifeInfo

class IndividualDetailsView(GenealogyDetailsView, LoginRequiredMixin, PermissionRequiredMixin):
    model = IndividualRecord
    form_class = EditIndividualForm
    template_name = 'family/individual/life.html'
    permission_required = 'family.change_pedigree'

    def get_template_names(self) -> List[str]:
        ret = super().get_template_names()
        view = self.kwargs.get('view', '')
        if view:
            ret = [f'family/individual/{view}.html']
        return ret
    
    def get_context_data(self):
        context = super().get_context_data()
        context['tree_id'] = self.kwargs.get('ft')
        view = self.kwargs.get('view', '')
        indi = self.get_object()
        if indi:
            match view:
                case 'life':
                    context['life_info'] = asdict(LifeInfo(indi))
        return context


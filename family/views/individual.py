from typing import List
from family.views.base import GenealogyDetailsView
from family.forms import EditIndividualForm
from family.models import IndividualRecord

class IndividualDetailsView(GenealogyDetailsView):
    model = IndividualRecord
    form_class = EditIndividualForm
    template_name = 'family/individual/life.html'

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
        indi = IndividualRecord(self.get_object())
        if indi:
            match view:
                case 'life':
                    context['life_info'] = indi.get_life_info()
        return context

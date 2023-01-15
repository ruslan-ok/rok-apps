from family.views.base import GenealogyDetailsView
from family.forms import EditIndividualForm
from family.models import IndividualRecord

class IndividualDetailsView(GenealogyDetailsView):
    model = IndividualRecord
    form_class = EditIndividualForm
    template_name = 'family/individual/detail.html'

    def get_context_data(self):
        context = super().get_context_data()
        return context

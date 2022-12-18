from family.views.base import GenealogyListView
from family.models import (FamTreeUser, )

class ReportListView(GenealogyListView):
    model = FamTreeUser
    template_name = 'family/reports.html'

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rusel.base.views import BaseListView
from task.const import APP_GENEA, ROLE_STEMMA, NUM_ROLE_STEMMA
from genea.models import Header
from genea.config import app_config
from genea.gedcom_551.exp import ExpGedcom551

app = APP_GENEA
role = ROLE_STEMMA

class StemmaListView(BaseListView):
    model = Header

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_STEMMA
        response = super().form_valid(form)
        return response

    def get_dataset(self, group, query=None, nav_item=None):
        return Header.objects.all()

    def tune_dataset(self, data, group):
        return Header.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def chart_family(request):
    return HttpResponse('Chart Family')
    
def chart_ancestors(request):
    return HttpResponse('Chart Ancestors')

def export(request, pk):
    folder = 'C:\\gedcom\\exp'
    mgr = ExpGedcom551(request)
    mgr.export_gedcom_551(folder, pk)
    return HttpResponseRedirect(reverse('genea:list'))

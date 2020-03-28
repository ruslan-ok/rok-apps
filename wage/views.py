from django.http import HttpResponse
from django.template import loader
from .models import Period
from xml.etree import cElementTree as ET
from django.contrib.auth.decorators import login_required, permission_required
from .wage_xml import import_all

def import_wage():
    return []

@login_required(login_url='account:login')
@permission_required('wage.view_person')
def index(request):
    imp_data  = []
    imp_errors = []
    import_all(imp_data, imp_errors)
    template = loader.get_template('wage_xml.html')
    context = {
        'xml': imp_data,
        'err': imp_errors,
        'xml_len': len(imp_data),
        'err_len': len(imp_errors),
        }
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:login')
@permission_required('wage.view_person')
def periods(request):
    per_list = Period.objects.order_by('dBeg')[:25]
    template = loader.get_template('wage/periods.html')
    context = {'per_list': per_list,}
    return HttpResponse(template.render(context, request))

#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Period
from xml.etree import cElementTree as ET
from .wage_xml import import_all

def import_wage():
    return []

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


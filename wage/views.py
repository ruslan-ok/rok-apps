#from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Period

def index(request):
    return HttpResponse("Hello, world. You're at the wage index.")

def periods(request):
    per_list = Period.objects.order_by('dBeg')[:25]
    template = loader.get_template('wage/periods.html')
    context = {'per_list': per_list,}
    return HttpResponse(template.render(context, request))

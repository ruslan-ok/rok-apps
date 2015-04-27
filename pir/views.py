# coding=UTF-8
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from pir.models import PirTable, PirData


@csrf_exempt
def pir_edit(request, tbl):
  if (request.method == 'GET'):
    try:
      t = PirTable.objects.get(name = tbl)
      d = PirData.objects.filter(table = t)
      text = []
      for r in d:
        text += r.rec
      return HttpResponse(text)
    except PirTable.DoesNotExist:
      return render(request, 'pir/pir.html', {})
  
  if (request.method == 'POST'):
    try:
      t = PirTable.objects.get(name = tbl)
    except PirTable.DoesNotExist:
      t = PirTable(name = tbl)
      t.save()
    PirData.objects.filter(table = t).delete()
    lines = request.readlines()
    for s in lines:
      r = PirData(table = t, rec = s)
      r.save()
  return render(request, 'pir/pir.html', {})

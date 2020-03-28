from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from pir.models import PirTable, PirPart, PirData
from django.contrib.auth.decorators import login_required, permission_required


def restore_DateList(request):
  lt = PirTable.objects.get(name = 'DateList')
  lp = PirPart.objects.get(table = lt)
  ld = PirData.objects.filter(table = lt).delete()

  for i in range(1, 1000):
    d = PirData(table = lt, part = lp, rec = str(i))
    d.save()
  
@csrf_exempt
@login_required(login_url='account:login')
@permission_required('pir.view_pirdata')
def pir_edit(request, tbl):
  table = tbl
  part = ''
  prefix = ''
  pos = tbl.find('_')

  if (pos != -1):
    if (tbl[0] >= '0') and (tbl[0] <= '9'):
      prefix = tbl[0:pos]
      table = tbl[(pos+1):]
    else:
      table = tbl[0:pos]
      part = tbl[(pos+1):]

  if (request.method == 'GET'):
    text = []

    try:
      t = PirTable.objects.get(name = table)
    except PirTable.DoesNotExist:
      return render(request, 'pir/pir.html', {})

    if (prefix == ''):
      try:
        p = PirPart.objects.get(table = t, name = part)
      except PirPart.DoesNotExist:
        p = PirPart(table = t, name = part)
        p.save()
    else:
      ps = PirPart.objects.filter(table = t)

      if (int(prefix) >= len(ps)):
        if (t.name == 'DateList') and (int(prefix) == 0):
          p = PirPart(table = t)
          p.save()
          ps = PirPart.objects.filter(table = t)
        else:
          text += 'NoDataFound'
          return HttpResponse(text)
      p = ps[int(prefix)]
      
    d = PirData.objects.filter(table = t, part = p)
    if ((t.name == 'DateList') and (len(d) < 10)):
      restore_DateList(request)
      d = PirData.objects.filter(table = t, part = p)
    for r in d:
      nn = ''
      ss = r.rec
      if (len(ss) > 0):
        if (ss[-1] != '\n'):
          nn = '\n'
      ss += nn
      if (p.name != ''):
        ss = p.name + ';' + r.rec + nn
      text.append(ss)
    return HttpResponse(text)
  
  if (request.method == 'POST'):
    try:
      t = PirTable.objects.get(name = table)
    except PirTable.DoesNotExist:
      t = PirTable(name = table)
      t.save()
    try:
      p = PirPart.objects.get(table = t, name = part)
    except PirPart.DoesNotExist:
      p = PirPart(table = t, name = part)
      p.save()
    PirData.objects.filter(table = t, part = p).delete()
    lines = request.readlines()
    for s in lines:
      r = PirData(table = t, part = p, rec = s)
      r.save()
  return render(request, 'pir/pir.html', {})

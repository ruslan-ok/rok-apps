from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from datetime import date, datetime
import datetime
from django.contrib.sites.shortcuts import get_current_site

from task.models import TGroup, TaskView, TaskFilter, FLTR_TERM, FLTR_GROUP, FLTR_IMPORTANCE, FLTR_COLOR, FLTR_COMPLETE, SORTS

class TaskViewForm(forms.ModelForm):
    code = forms.CharField(required = False)
    grp = forms.ModelChoiceField(queryset = TGroup.objects.all(), required = False, empty_label = '------ без группы ------')
    class Meta:
        model = TaskView
        exclude = ['id', 'user', 'fltr', 'sort', 'grp', 'flds', 'active']

#============================================================================
def edit_context(request, form, pk, vw, fltr, debg):
    form.fields['grp'].queryset = TGroup.objects.filter(user = request.user.id)
    views = TaskView.objects.filter(user = request.user.id).order_by('code', 'name')
    fltr_t = TaskFilter.objects.filter(view = vw, entity = FLTR_TERM).order_by('npp')       #Срок
    fltr_g = TaskFilter.objects.filter(view = vw, entity = FLTR_GROUP).order_by('npp')      #Группа
    fltr_i = TaskFilter.objects.filter(view = vw, entity = FLTR_IMPORTANCE).order_by('npp') #Важность
    fltr_r = TaskFilter.objects.filter(view = vw, entity = FLTR_COLOR).order_by('npp')      #Цвет
    fltr_c = TaskFilter.objects.filter(view = vw, entity = FLTR_COMPLETE).order_by('npp')   #Исполнение
    sorts  = TaskFilter.objects.filter(view = vw, entity = SORTS).order_by('npp')           #Сортировки

    context = {'views':  views, 
               'form':   form, 
               'pid':    pk,
               'fltr':   77,
               'fltr_t': fltr_t,
               'fltr_g': fltr_g,
               'fltr_i': fltr_i,
               'fltr_r': fltr_r,
               'fltr_c': fltr_c,
               'sorts':  sorts,
               'sort':   88,
               'flds':   99,
               'debg':   debg,
               'title':   'Представления',
               'site_header': get_current_site(request).name,
              }
    return context

def SaveFilters(fltrs, ent, vw, values, directs):
  n = 1
  i = 1
  while (i < len(values)) and (values[i] != ']'):
    s = '';
    while (values[i] >= '0') and (values[i] <= '9'):
      s += values[i]
      i += 1
    f = TaskFilter(view = vw)
    #f.view   = vw
    f.entity = ent
    f.npp    = n
    f.value  = int(s)
    if (len(directs) > 0):
      f.direct = int(directs[1+(n-1)*2])
    f.save()
    n += 1
    if (values[i] == ','):
      i += 1

#============================================================================
def do_view(request, pk):
  if (request.method == 'GET'):
    if (pk > 0):
      vw = get_object_or_404(TaskView, pk = pk)
      form = TaskViewForm(instance = vw)
      context = edit_context(request, form, pk, vw.id, vw.fltr, 'get-0')
    else:
      form = TaskViewForm(initial = {'name': ''})
      context = edit_context(request, form, pk, 0, 0, 'get-1: pk=0')
    return render(request, 'task/view.html', context)
  else:
    action = request.POST.get('action', False)
    
    act = 0
    if (action == 'Отменить'):
      act = 1
    else:
      if (action == 'Добавить') or (action == '+'):
        act = 2
      else:
        if (action == 'Сохранить'):
          act = 3
        else:
          if (action == 'Удалить'):
            act = 4
          else:
            act = 5

    if (act > 1):
      form = TaskViewForm(request.POST)

      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, pk, 0, 0, 'post-error')# + str(form.non_field_errors))
        return render(request, 'task/view.html', context)
      else:
        t = form.save(commit = False)

        if (act == 2):
          t.user = request.user
          t.save()

        if (act == 3):
          t.id = pk
          t.user = request.user
          t.save()

          vw = get_object_or_404(TaskView, pk = pk)
          fltrs = TaskFilter.objects.filter(view = vw)
          fltrs.delete();
          
          SaveFilters(fltrs, FLTR_TERM,       vw, request.POST.get('ret_fltr_0', False), '')
          SaveFilters(fltrs, FLTR_GROUP,      vw, request.POST.get('ret_fltr_1', False), '')
          SaveFilters(fltrs, FLTR_IMPORTANCE, vw, request.POST.get('ret_fltr_2', False), '')
          SaveFilters(fltrs, FLTR_COLOR,      vw, request.POST.get('ret_fltr_3', False), '')
          SaveFilters(fltrs, FLTR_COMPLETE,   vw, request.POST.get('ret_fltr_4', False), '')
          SaveFilters(fltrs, SORTS,           vw, request.POST.get('ret_fltr_5', False), request.POST.get('ret_dirs', False))

        if (act == 4):
          t = get_object_or_404(TaskView, id = pk)
          t.delete()

    if (pk > 0) or (act == 1):
      return HttpResponseRedirect(reverse('task:view_view'))
    else:
      return render(request, 'task/view.html', context)


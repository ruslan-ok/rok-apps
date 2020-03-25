from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from datetime import date, datetime
import datetime

from task.models import TGroup

class GroupForm(forms.ModelForm):
    class Meta:
        model = TGroup
        exclude = ['id', 'user', 'sort', 'active']


#============================================================================
def edit_context(request, form, pk, debg):
    groups = TGroup.objects.filter(user = request.user.id).order_by('name')
    context = {'groups': groups, 
               'form':   form, 
               'pid':    pk,
               'debg':   debg,
              }
    return context

#============================================================================
def do_grps(request, pk):
  if (request.method == 'GET'):
    if (pk > 0):
      grp = get_object_or_404(TGroup, pk = pk)
      form = GroupForm(instance = grp)
    else:
      form = GroupForm(initial = {'name': ''})
    context = edit_context(request, form, pk, 'get-0')
    return render(request, 'task/grps.html', context)
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
      form = GroupForm(request.POST)

      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, pk, 'post-error')# + str(form.non_field_errors))
        return render(request, 'task/grps.html', context)
      else:
        t = form.save(commit = False)

        if (act == 2):
          t.user = request.user
          t.save()

        if (act == 3):
          t.id = pk
          t.user = request.user
          t.save()

        if (act == 4):
          t = get_object_or_404(TGroup, id = pk)
          t.delete()

    if (pk > 0) or (act == 1):
      return HttpResponseRedirect(reverse('task:grps_view'))
    else:
      return render(request, 'task/grps.html', context)


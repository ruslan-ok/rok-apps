# coding=UTF-8
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.forms import ModelForm
from proj.models import Direct


class DirectForm(ModelForm):
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    active = forms.IntegerField(u'Активное', required = False)
    class Meta:
        model = Direct
        fields = ('name', 'active', 'action')

#============================================================================
def edit_context(_request, _form, _pid, _debug_text):
    dirs = Direct.objects.filter(user = _request.user.id)
    return { 'dirs': dirs, 
             'form': _form, 
             'pid': _pid,
             'app_text':  u'Приложения', 
             'proj_text': u'Операции', 
             'page_title': u'Направления проектов', 
             'dirs_count': dirs.count,
             'debug_text': _debug_text,
           }
#============================================================================
def do_dirs(request, pk):
  if (request.method == 'GET'):
    if (pk > 0):
      t = get_object_or_404(Direct, pk=pk)
      form = DirectForm(instance = t)
    else:
      form = DirectForm(initial = {'name': '', 'active': 0})
    context = edit_context(request, form, pk, 'get-1')
    return render(request, 'proj/dirs.html', context)
  else:
    action = request.POST.get('action', False)
    active = request.POST.get('active', False)
    
    act = 0
    if (action == u'Отменить'):
      act = 1
    else:
      if (action == u'Добавить'):
        act = 2
      else:
        if (action == u'Сохранить'):
          act = 3
        else:
          if (action == u'Удалить'):
            act = 4
          else:
            act = 5

    if (act > 1):
      form = DirectForm(request.POST)
      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, pk, 'post-error' + str(form.non_field_errors))
        return render(request, 'proj/dirs.html', context)
      else:
        t = form.save(commit=False)

        if (act < 4):
          if (int(active) > 0):
            active_dirs = Direct.objects.filter(user = request.user.id, active = 1)
            for c in active_dirs:
              c.active = 0
              c.save()

        if (act == 2):
          t.user = request.user
          t.active = int(active)
          t.save()

        if (act == 3):
          t.id = pk
          t.user = request.user
          t.active = int(active)
          t.save()

        if (act == 4):
          t = get_object_or_404(Direct, id=pk)
          t.delete()

    return HttpResponseRedirect(reverse('proj:dirs_view'))


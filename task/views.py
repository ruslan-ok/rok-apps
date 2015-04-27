# coding=UTF-8
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django import forms
from datetime import date, datetime
import datetime

from task.models import Task

class TaskForm(forms.ModelForm):
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    id = forms.IntegerField(widget = forms.HiddenInput, required = False)
    due_d = forms.DateField(required = False)
    due_t = forms.TimeField(required = False)
    class Meta:
        model = Task
        fields = ['id', 'name', 'comment']


#============================================================================
def edit_context(request, form, task_id, _deb_text):
    tasks = Task.objects.filter(user = request.user.id).order_by('-due_date')[:20]
    context = {'tasks': tasks, 
               'form': form, 
               'pid':  task_id,
               'debug_text': _deb_text,
               'app_text': u'Приложения',
               'page_title': 'Задачи',
               'task_summary': '',
               }
    return context

#============================================================================
def do_task(request, task_id):
  if (request.method == 'GET'):
    if (task_id > 0):
      task = get_object_or_404(Task, pk = task_id)
      form = TaskForm(instance = task)
      context = edit_context(request, form, task_id, 'get-1')
      return render(request, 'task/task_edit.html', context)
    else:
      form = TaskForm(initial = {'name': ''})
      context = edit_context(request, form, 0, 'get-0')
      return render(request, 'task/task.html', context)
  else:
    action = request.POST.get('action', False)
    saction = request.POST['action']
    
    act = 0
    if (action == u'Отменить'):
      act = 1
    else:
      if (action == u'Добавить') or (action == '+'):
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
      form = TaskForm(request.POST)

      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, task_id, 'post-error' + str(form.non_field_errors))
        return render(request, 'task/task_edit.html', context)
      else:
        t = form.save(commit = False)

        if (act == 2):
          t.user = request.user
          t.pub_date = date.today()
          t.save()

        if (act == 3):
          t.id = task_id
          t.user = request.user
          t.pub_date = date.today()
          t.save()

        if (act == 4):
          t = get_object_or_404(Task, id = task_id)
          t.delete()

    if (task_id > 0) or (act == 1):
      return HttpResponseRedirect(reverse('task:task_view'))
    else:
      return render(request, 'task/task_edit.html', context)

#============================================================================
@login_required
def task_view(request):
    return do_task(request, 0)

#============================================================================
@login_required
def task_edit(request, pk):
    return do_task(request, pk)



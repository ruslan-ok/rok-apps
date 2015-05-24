# coding=UTF-8
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django import forms
from datetime import date, datetime, timedelta

from task.models import Task, TGroup

CHOICES = ( ('0', 'один раз'),
            ('1', 'ежедневно'),
            ('2', 'еженедельно'),
            ('3', 'ежемесячно'),
            ('4', 'ежегодно'),
)

class TaskForm(forms.ModelForm):
    name   = forms.CharField(help_text = 'Наименование', required = True)
    code   = forms.CharField(help_text = 'Код', required = False)
    grp    = forms.ModelChoiceField(queryset = TGroup.objects.all(), required = False, empty_label = '------ без группы ------')
    d_exec = forms.DateField(required = False)
    t_exec = forms.TimeField(required = False)
    repeat = forms.ChoiceField(required = False, choices = CHOICES)
    cycle  = forms.IntegerField(required = False)
    step   = forms.IntegerField(required = False)
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    id = forms.IntegerField(widget = forms.HiddenInput, required = False)
    class Meta:
        model = Task
        exclude = ['user', 'pub_date', 'value1', 'value2', 
                   'done', 'start', 'stop_mode', 'count', 'stop', 'active', 'attrib']

#============================================================================
def edit_context_view(request, form, debg):
    form.fields['grp'].queryset = TGroup.objects.filter(user = request.user.id)
    tasks = Task.objects.filter(user = request.user.id).order_by('-d_exec', '-t_exec')[:20]
    context = {'tasks': tasks, 
               'form':  form, 
               'debg':  debg,
              }
    return context

#============================================================================
def edit_context_edit(request, form, pk, debg):
    form.fields['grp'].queryset = TGroup.objects.filter(user = request.user.id)
    context = {'form':  form, 
               'pid':   pk,
               'debg':  debg,
              }
    return context

#============================================================================
def do_task(request, task_id):
  if (request.method == 'GET'):
    if (task_id > 0):
      task = get_object_or_404(Task, pk = task_id)
      d = ''
      t = ''
      if (task.d_exec != None):
        d = task.d_exec.isoformat()
      if (task.t_exec != None):
        t = task.t_exec.isoformat()
      form = TaskForm(instance = task, 
                      initial = {'d_exec': d,
                                 't_exec': t,})
      context = edit_context_edit(request, form, task_id, 'get-1')
      return render(request, 'task/task_edit.html', context)
    else:
      form = TaskForm(initial = {'name': '', 'active': 1})
      context = edit_context_view(request, form, 'get-0')
      return render(request, 'task/task.html', context)
  else:
    action = request.POST.get('action', False)
    
    act = 0
    if (action == u'C'):
      act = 1
    else:
      if (action == u'A') or (action == '+'):
        act = 2
      else:
        if (action == u'S'):
          act = 3
        else:
          if (action == u'D'):
            act = 4
          else:
            act = 5

    if (act > 1):
      form = TaskForm(request.POST)

      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context_edit(request, form, task_id, 'post-error')# + str(form.non_field_errors))
        return render(request, 'task/task_edit.html', context)
      else:
        t = form.save(commit = False)
        td = request.POST.get('d_exec', False)
        tt = request.POST.get('t_exec', False)
        t.d_exec = None
        t.t_exec = None

        if (td != '') and (td != False):
          t.d_exec = datetime.strptime(td, '%Y-%m-%d')

        if (tt != '') and (tt != False):
          t.t_exec = datetime.strptime(tt, '%H:%M')# + timedelta(hours = 3)

        if (act == 2):
          t.user = request.user
          t.pub_date = date.today()
          t.active = 1
          t.attrib = 0
          t.save()

        if (act == 3):
          t.id = task_id
          t.user = request.user
          t.attrib = 0
          t.save()

        if (act == 4):
          t = get_object_or_404(Task, id = task_id)
          t.delete()

        #context = edit_context_edit(request, form, task_id, 'check test: ' + test)
        #return render(request, 'task/task_edit.html', context)

    if (task_id > 0) or (act == 1):
      return HttpResponseRedirect(reverse('task:task_view'))
    else:
      context = edit_context_edit(request, form, task_id, 'cancel')
      return render(request, 'task/task_edit.html', context)


from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from datetime import date, datetime, timedelta
from hier.utils import get_base_context
from .models import Fuel, Car, Part, Repl


debug_text = ''


#============================================================================
class ReplForm(forms.ModelForm):
    class Meta:
        model = Repl
        exclude = ('part', 'oper',)

#============================================================================
def edit_context(request, form, folder_id, _part, _repl):
    part = Part.objects.get(id = _part)
    replaces = Repl.objects.filter(part = _part).order_by('-dt_chg')[:20]
    context = get_base_context(request, folder_id, _repl, 'Замены расходника ' + part.name)
    context['form'] =       form 
    context['replaces'] =   replaces 
    context['part'] =       _part 
    context['app_text'] =   'Приложения' 
    context['page_title'] = 'Замены расходника ' + part.name 
    context['part_text'] =  'Список расходников' 
    return context

#============================================================================
def do_repl(request, folder_id, pt, content_id):
    if (pt == 0):
      return HttpResponseRedirect(reverse('fuel:part_list', args = [folder_id]))

    part = Part.objects.get(id = pt)

    if (part == None):
      return HttpResponseRedirect(reverse('fuel:part_list', args = [folder_id]))

    if (request.method == 'GET'):
      if (content_id > 0):
        # Отображение конкретной записи
        t = get_object_or_404(Repl, id = content_id)
        ttt = t.dt_chg.date()
        form = ReplForm(instance = t,
                        initial={'dt_chg': ttt.isoformat()})
        context = edit_context(request, form, folder_id, pt, content_id)
      else:
        # Пустая форма для новой записи
        last = Fuel.objects.filter(car = part.car).order_by('-pub_date')[:1]
        odo = 0
        if (len(last) > 0):
          odo = last[0].odometr
        form = ReplForm(initial={'part':     part,
                                 'dt_chg':   date.today().isoformat(),
                                 'odometr':  odo,
                                 'manuf':    '',
                                 'part_num': '',
                                 'name':     '',
                                 'comment':  '',
                                 'debug_text': 'pt = ' + str(pt)})
        context = edit_context(request, form, folder_id, pt, content_id)
      return render(request, 'fuel/repl.html', context)
    else:
      action = request.POST.get('action', False)
      
      act = 0
      if (action == 'Отменить'):
        act = 1
      else:
        if (action == 'Добавить'):
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
        form = ReplForm(request.POST)
        if not form.is_valid():
          # Ошибки в форме, отобразить её снова
          context = edit_context(request, form, folder_id, pt, content_id)
          return render(request, 'fuel/repl.html', context)
        else:
          t = form.save(commit = False)
    
          if (act == 2):
            t.part = part
            t.dt_chg = t.dt_chg + timedelta(days=1)
            t.save()
    
          if (act == 3):
            t.id = content_id
            t.part = part
            t.dt_chg = t.dt_chg + timedelta(days=1)
            t.save()
    
          if (act == 4):
            t = get_object_or_404(Repl, id=content_id)
            t.delete()
    
      return HttpResponseRedirect(reverse('fuel:repl_list', args = [folder_id, pt]))

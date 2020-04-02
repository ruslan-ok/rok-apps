from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from datetime import date, datetime, timedelta
from django.forms import ModelForm
from django.contrib.sites.shortcuts import get_current_site
from proj.models import Direct, Proj, proj_summary


debug_text = ''


#============================================================================
class ProjForm(ModelForm):
    class Meta:
        model = Proj
        exclude = ('direct',)

#============================================================================
def edit_context(request, form, adir, pid, debug_text):
    opers = Proj.objects.filter(direct = adir).order_by('-date')[:20]
    curdir = Direct.objects.get(user = request.user.id, active = 1)
    dirs = Direct.objects.filter(user = request.user.id, active = 0)
    return { 'form':          form, 
             'opers':         opers, 
             'dirs':          dirs, 
             'pid':           pid, 
             'app_text':    'Приложения', 
             'direct_text': 'Проектные направления', 
             'title':  'Операции проекта ' + curdir.name, 
             'site_header': get_current_site(request).name,
             'page_title':  'Операции проекта ' + curdir.name, 
             'proj_summary':  proj_summary(request.user),
             'total_count':   Proj.objects.filter(direct = adir).count,
             'debug_text':    debug_text, 
           }
#============================================================================
def do_proj(request, pk):
    try:
      adir = Direct.objects.get(user = request.user.id, active = 1)
    except Direct.DoesNotExist:
      dirs = Direct.objects.filter(user = request.user.id, active = 0)
      if (len(dirs) == 0):
        adir = None
      else:
        adir = dirs[0]
        adir.active = 1
        adir.save()
    
    if (adir == None):
      return HttpResponseRedirect(reverse('proj:dirs_edit', args=(0,)))

    if (request.method == 'GET'):
      ttt = date.today()
      if (pk > 0):
        # Отображение конкретной записи
        t = get_object_or_404(Proj, pk=pk)
        ttt = t.date.date()
        form = ProjForm(instance = t,
                        initial={'date': ttt.isoformat()})
      else:
        # Пустая форма для новой записи
        form = ProjForm(initial={'direct': adir, 
                                 'date': date.today().isoformat(),
                                 'kol': 1,
                                 'price': 0,
                                 'course': 0,
                                 'usd': 0,
                                 'kontr': '',
                                 'text': '',
                                })

      context = edit_context(request, form, adir, pk, ttt.isoformat())
      return render(request, 'proj/proj.html', context)
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
        form = ProjForm(request.POST)
        if not form.is_valid():
          # Ошибки в форме, отобразить её снова
          context = edit_context(request, form, adir, pk, 'post-error' + str(form.non_field_errors))
          return render(request, 'proj/proj.html', context)
        else:
          t = form.save(commit=False)
    
          if (act == 2):
            t.direct = adir
            t.date = t.date + timedelta(days=1)
            t.save()
    
          if (act == 3):
            t.id = pk
            t.direct = adir
            t.date = t.date + timedelta(days=1)
            t.save()
    
          if (act == 4):
            t = get_object_or_404(Proj, id=pk)
            t.delete()
    
      return HttpResponseRedirect(reverse('proj:proj_view'))

def do_change_dir(request, pk):
    active_dirs = Direct.objects.filter(user = request.user.id, active = 1)
    for c in active_dirs:
      c.active = 0
      c.save()
    adir = Direct.objects.get(id = pk)
    adir.active = 1
    adir.save()
    return HttpResponseRedirect(reverse('proj:proj_view'))

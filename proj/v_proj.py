from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from datetime import date, datetime, timedelta
from django.forms import ModelForm

from hier.utils import get_base_context
from proj.models import Direct, Proj, proj_summary


#----------------------------------
class ProjForm(ModelForm):
    class Meta:
        model = Proj
        exclude = ('direct',)

#----------------------------------
def edit_context(request, form, adir, folder_id, content_id):
    opers = Proj.objects.filter(direct = adir).order_by('-date')[:20]
    curdir = Direct.objects.get(user = request.user.id, active = 1)
    dirs = Direct.objects.filter(user = request.user.id, active = 0)
    context = get_base_context(request, folder_id, content_id, 'Операции проекта ' + curdir.name)
    context['form'] = form
    context['opers'] = opers
    context['dirs'] = dirs
    context['proj_summary'] = proj_summary(request.user)
    context['total_count'] = Proj.objects.filter(direct = adir).count
    return context

#----------------------------------
def do_proj(request, folder_id, content_id):
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
        return HttpResponseRedirect(reverse('proj:dirs_form', args = [folder_id, 0]))

    if (request.method == 'GET'):
        ttt = date.today()
        if (content_id > 0):
            # Отображение конкретной записи
            t = get_object_or_404(Proj, id = content_id)
            ttt = t.date.date()
            form = ProjForm(instance = t, initial = { 'date': ttt.isoformat() })
        else:
            # Пустая форма для новой записи
            form = ProjForm(initial = { 'direct': adir, 'date': date.today().isoformat(), 'kol': 1, 'price': 0, 'course': 0, 'usd': 0, 'kontr': '', 'text': '' })
          
        context = edit_context(request, form, adir, folder_id, content_id)
        return render(request, 'proj/proj.html', context)
    else:
        action = request.POST.get('action', False)
        
        act = 0
        if (action == 'Отменить'):
            act = 1
        elif (action == 'Добавить'):
            act = 2
        elif (action == 'Сохранить'):
            act = 3
        elif (action == 'Удалить'):
            act = 4
        else:
            act = 5
      
        if (act > 1):
            form = ProjForm(request.POST)
            if not form.is_valid():
                # Ошибки в форме, отобразить её снова
                context = edit_context(request, form, adir, folder_id, content_id)
                return render(request, 'proj/proj.html', context)
            else:
                t = form.save(commit = False)
              
                if (act == 2):
                    t.direct = adir
                    t.date = t.date + timedelta(days = 1)
                    t.save()
              
                if (act == 3):
                    t.id = content_id
                    t.direct = adir
                    t.date = t.date + timedelta(days = 1)
                    t.save()
              
                if (act == 4):
                    t = get_object_or_404(Proj, id = content_id)
                    t.delete()
      
        return HttpResponseRedirect(reverse('proj:proj_list', args = [folder_id]))

#----------------------------------
def do_change_dir(request, folder_id, content_id):
    active_dirs = Direct.objects.filter(user = request.user.id, active = 1)
    for c in active_dirs:
        c.active = 0
        c.save()
    adir = Direct.objects.get(id = content_id)
    adir.active = 1
    adir.save()
    return HttpResponseRedirect(reverse('proj:proj_list', args = [folder_id]))

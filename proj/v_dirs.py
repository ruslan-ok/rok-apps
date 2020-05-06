from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.forms import ModelForm

from hier.utils import get_base_context
from proj.models import Direct


#----------------------------------
class DirectForm(ModelForm):
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    active = forms.IntegerField(label = 'Активное', required = False)
    class Meta:
        model = Direct
        fields = ('name', 'active', 'action')

#----------------------------------
def do_dirs(request, folder_id, content_id):
    context = get_base_context(request, folder_id, content_id, 'Направления проектов')
    dirs = Direct.objects.filter(user = request.user.id)
    context['dirs'] = dirs
    context['dirs_count'] = dirs.count

    if (request.method == 'GET'):
        if (content_id > 0):
            t = get_object_or_404(Direct, id = content_id)
            form = DirectForm(instance = t)
        else:
            form = DirectForm(initial = {'name': '', 'active': 0})
        context['form'] = form
        return render(request, 'proj/dirs.html', context)
    else:
        action = request.POST.get('action', False)
        active = request.POST.get('active', False)
        
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
            form = DirectForm(request.POST)
            if not form.is_valid():
                # Ошибки в форме, отобразить её снова
                context['form'] = form
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
                    t.id = content_id
                    t.user = request.user
                    t.active = int(active)
                    t.save()
              
                if (act == 4):
                    t = get_object_or_404(Direct, id = content_id)
                    t.delete()
      
        return HttpResponseRedirect(reverse('proj:dirs_list', args = [folder_id]))


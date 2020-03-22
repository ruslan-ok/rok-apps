from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from trip.models import Person

class PersForm(ModelForm):
    me = forms.IntegerField(label = 'Я', required = False)
    class Meta:
        model = Person
        fields = ('name', 'dative', 'me')

#============================================================================
def edit_context(_request, _form, _pid, _debug_text):
    pers = None
    if (_pid > 0):
      pers = Person.objects.get(id = _pid)
    persons = Person.objects.filter(user = _request.user.id)
    return { 'persons': persons, 
             'form': _form, 
             'pid': _pid,
             'app_text':   u'Приложения', 
             'trip_text':  u'Проезд',
             'page_title': u'Водители и пассажиры', 
             'pers_count': persons.count,
             'debug_text': _debug_text,
             'cur':        pers,
             'pers':       persons
           }
#============================================================================
def do_pers(request, pk):
  if (request.method == 'GET'):
    if (pk > 0):
      t = get_object_or_404(Person, pk=pk)
      form = PersForm(instance = t)
    else:
      form = PersForm(initial = {'name': '', 'dative': '', 'me': 0})
    context = edit_context(request, form, pk, 'get-1')
    return render(request, 'trip/pers.html', context)
  else:
    action = request.POST.get('action', False)
    me = request.POST.get('me', False)
   
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
      form = PersForm(request.POST)
      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, pk, 'post-error: ' + str(form.non_field_errors))
        return render(request, 'trip/pers.html', context)
      else:
        t = form.save(commit=False)

        if (act < 4):
          if (int(me) > 0):
            active_pers = Person.objects.filter(user = request.user.id, me = 1)
            for p in active_pers:
              p.me = 0
              p.save()

        if (act == 2):
          t.user = request.user
          t.me = int(me)
          t.save()

        if (act == 3):
          t.id = pk
          t.user = request.user
          t.me = int(me)
          t.save()

        if (act == 4):
          t = get_object_or_404(Person, id=pk)
          t.delete()

    return HttpResponseRedirect(reverse('trip:pers_view'))


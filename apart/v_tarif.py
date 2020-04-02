from django.shortcuts import get_object_or_404, render
from django import forms
from django.template import loader
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from datetime import date
from django.forms import ModelForm
from django.contrib.sites.shortcuts import get_current_site
from rusel.const import t_months
from apart.models import Tarif


class TarifForm(ModelForm):
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    id = forms.IntegerField(widget = forms.HiddenInput, required = False)
    month = forms.IntegerField(label = 'Месяц', required = True, initial = date.today().month, widget=forms.Select(choices=t_months))
    year = forms.IntegerField(label = 'Год', required = True, initial = date.today().year)
    class Meta:
        model = Tarif
        fields = ('resource', 'month', 'year', 'tarif', 'border', 'tarif2', 'border2', 'tarif3', 'text')

def do_tarif(request, pk):
    if (request.method == 'POST'):
        action = request.POST['action']
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
          form = TarifForm(request.POST)
          if form.is_valid():
            t = form.save(commit=False)

            if (act == 2):
              t.user = request.user
              t.period = int(request.POST['year'])*100 + int(request.POST['month'])
              t.attrib = 0
              t.save()

            if (act == 3):
              t.id = pk
              t.user = request.user
              t.period = int(request.POST['year'])*100 + int(request.POST['month'])
              t.attrib = 0
              t.save()

            if (act == 4):
              t = get_object_or_404(Tarif, id=pk)
              t.delete()

        return HttpResponseRedirect(reverse('apart:tarif_view', args=()))
    else:
        if (pk > 0):
          t = get_object_or_404(Tarif, pk=pk)
          form = TarifForm(instance=t)
        else:
          form = TarifForm()
        tarifs = Tarif.objects.filter(user = request.user.id).order_by('-period', 'resource')
        form.fields['resource'].label = 'Ресурс'
        context = {
            'tarifs': tarifs, 
            'form': form, 
            'app_text': 'Приложения', 
            'apart_text': 'Коммуналка', 
            'title': 'Тарифы', 
            'page_title': 'Тарифы', 
            'pid': str(pk),
            'site_header': get_current_site(request).name,
            }
        template = loader.get_template('apart/tarif.html')
        return HttpResponse(template.render(context, request))



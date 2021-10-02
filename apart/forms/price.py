from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from apart.config import app_config
from apart.models import Apart, Price, Service

role = 'price'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    start = forms.DateField(
        label=_('valid from').capitalize(),
        required=True,
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control date d-inline-block mb-3 me-3', 'type': 'date'}))
    service = forms.ModelChoiceField(
        label=_('service').capitalize(),
        required=True,
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
    tarif = forms.DecimalField(
        label=_('tarif').capitalize(),
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    border = forms.IntegerField(
        label=_('border').capitalize(),
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    tarif2 = forms.DecimalField(
        label=_('tarif 2').capitalize(),
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    border2 = forms.IntegerField(
        label=_('border 2').capitalize(),
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))
    tarif3 = forms.DecimalField(
        label=_('tarif 3').capitalize(),
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Task
        fields = ['start', 'service', 'tarif', 'border', 'tarif2', 'border2', 'tarif3', 'info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        apart = Apart.objects.filter(user=kwargs['instance'].user.id, active=True).get()
        self.fields['service'].queryset = Service.objects.filter(apart=apart)
        if Price.objects.filter(task=kwargs['instance'].id).exists():
            price = Price.objects.filter(task=kwargs['instance'].id).get()
            self.fields['service'].initial = price.serv.id
            self.fields['tarif'].initial = price.tarif
            self.fields['border'].initial = price.border
            self.fields['tarif2'].initial = price.tarif2
            self.fields['border2'].initial = price.border2
            self.fields['tarif3'].initial = price.tarif3

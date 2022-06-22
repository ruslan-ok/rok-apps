from django import forms
from django.utils.translation import gettext_lazy as _, gettext

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, NumberInput, UrlsInput
from task.models import Task
from apart.config import app_config

role = 'bill'

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
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Period'), 'type': 'date'}))
    event = forms.DateTimeField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('Date of payment'), 'type': 'datetime-local'}))
    bill_rate = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('US dollar exchange rate'), 'step': '0.0001'}))
    bill_residents = forms.IntegerField(
        label=False,
        required=True,
        widget=NumberInput(attrs={'label': _('Number of residents'), 'step': '1'}))
    bill_tv_bill = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_tv_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_phone_bill = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_phone_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_zhirovka = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_zkx_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_poo = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_poo_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_el_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_gas_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    bill_water_pay = forms.DecimalField(label=False, required=False, widget=forms.NumberInput(attrs={'step': '0.01'}))
    info = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea(attrs={'label': _('Comment'), 'class': 'form-control mb-1', 'data-autoresize':''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))

    class Meta:
        model = Task
        fields = ['start', 'event', 'bill_rate', 'bill_residents', 
                  'bill_tv_bill', 'bill_tv_pay', 'bill_phone_bill', 'bill_phone_pay', 'bill_zhirovka', 'bill_zkx_pay', 
                  'bill_poo', 'bill_poo_pay', 'bill_el_pay', 'bill_water_pay', 'bill_gas_pay', 'info', 'url',
                 ]

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

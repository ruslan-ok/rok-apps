from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, Select, NumberInput, UrlsInput
from task.const import APART_SERVICE
from task.models import Task
from apart.config import app_config

role = 'price'

#----------------------------------
class CreateForm(BaseCreateForm):

    new_service = forms.ChoiceField(
        label=False,
        required=True,
        widget=Select(attrs={'label': _('Service'), 'class': 'col-md-3'}))

    class Meta:
        model = Task
        fields = ['new_service']

    def __init__(self, nav_item, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        service_choices = []
        if nav_item.apart_has_el:
            service_choices.append((1, 'электроснабжение'),)
        if nav_item.apart_has_gas:
            service_choices.append((2, 'газоснабжение'),)
        if nav_item.apart_has_hw or nav_item.apart_has_cw:
            service_choices.append((4, 'водоснабжение'),)
            service_choices.append((5, 'водоотведение'),)
        self.fields['new_service'].choices = service_choices
        
#----------------------------------
class EditForm(BaseEditForm):
    start = forms.DateField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Valid from'), 'type': 'date'}))
    service_name = forms.CharField(
        label=_('Service'), 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control col-md-3', 'readonly': ''}))
    price_tarif = forms.DecimalField(
        label=False,
        required=True,
        widget=NumberInput(attrs={'label': _('Tarif'), 'class': 'mb-1', 'step': '0.00001'}))
    price_border = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Border'), 'class': 'mb-1', 'step': '0.0001'}))
    price_tarif2 = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Tarif 2'), 'class': 'mb-1', 'step': '0.00001'}))
    price_border2 = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Border 2'), 'class': 'mb-1', 'step': '0.0001'}))
    price_tarif3 = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Tarif 3'), 'class': 'mb-1', 'step': '0.00001'}))
    info = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-1', 'data-autoresize':''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))

    class Meta:
        model = Task
        fields = ['start', 'service_name', 'price_tarif', 'price_border', 'price_tarif2', 'price_border2', 'price_tarif3', 'info', 'url']

    def check_none(self, value):
        if value:
            return value
        return 0

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.fields['service_name'].initial = APART_SERVICE[kwargs['instance'].price_service]
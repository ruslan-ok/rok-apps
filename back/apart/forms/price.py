from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, Select, NumberInput, UrlsInput
from apart.const import APART_SERVICE, apart_service_name_by_id
from apart.models import ApartService, ApartPrice
from apart.config import app_config
from task.const import NUM_ROLE_SERV_PROP

role = 'price'

#----------------------------------
class CreateForm(BaseCreateForm):

    new_service = forms.ChoiceField(
        label=False,
        required=True,
        widget=Select(attrs={'label': _('Service'), 'class': 'col-md-3', 'style': 'width:180px;'}))

    class Meta:
        model = ApartPrice
        fields = ['new_service']

    def __init__(self, nav_item, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        service_sorts = {}
        for service in ApartService.objects.filter(user=nav_item.user.id, app_apart=NUM_ROLE_SERV_PROP, task_1=nav_item.id).order_by('sort'):
            if service.name not in service_sorts.keys():
                service_sorts[service.name] = service.sort if service.sort else ''
            else:
                if service_sorts[service.name] < service.sort:
                    service_sorts[service.name] = service.sort if service.sort else ''
        service_codes = [code for code in service_sorts]
        service_codes = sorted(service_codes, key=lambda x: service_sorts[x])
        service_choices = [(APART_SERVICE[code][0], APART_SERVICE[code][1]) for code in service_codes]
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
        model = ApartPrice
        fields = ['start', 'service_name', 'price_tarif', 'price_border', 'price_tarif2', 'price_border2', 'price_tarif3', 'info', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.fields['service_name'].initial = apart_service_name_by_id(kwargs['instance'].price_service)

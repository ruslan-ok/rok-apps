from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, Select, NumberInput, UrlsInput
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
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('valid from').capitalize(), 'type': 'date'}))
    service = forms.ModelChoiceField(
        label=False,
        required=True,
        queryset=None,
        widget=Select(attrs={'label': _('service').capitalize(), 'class': 'col-md-3'}))
    tarif = forms.DecimalField(
        label=False,
        required=True,
        widget=NumberInput(attrs={'label': _('tarif').capitalize(), 'class': 'mb-1', 'step': '0.00001'}))
    border = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('border').capitalize(), 'class': 'mb-1', 'step': '0.0001'}))
    tarif2 = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('tarif 2').capitalize(), 'class': 'mb-1', 'step': '0.00001'}))
    border2 = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('border 2').capitalize(), 'class': 'mb-1', 'step': '0.0001'}))
    tarif3 = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('tarif 3').capitalize(), 'class': 'mb-1', 'step': '0.00001'}))
    info = forms.CharField(
        label=_('comment').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-1', 'data-autoresize':''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))

    class Meta:
        model = Task
        fields = ['start', 'service', 'tarif', 'border', 'tarif2', 'border2', 'tarif3', 'info', 'url']

    def check_none(self, value):
        if value:
            return value
        return 0

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        apart = Apart.objects.filter(user=kwargs['instance'].user.id, active=True).get()
        self.fields['service'].queryset = Service.objects.filter(apart=apart)
        if Price.objects.filter(task=kwargs['instance'].id).exists():
            price = Price.objects.filter(task=kwargs['instance'].id).get()
            serv_id = 0
            if price.serv:
                serv_id = price.serv.id
            self.fields['service'].initial = serv_id
            self.fields['tarif'].initial = self.check_none(price.tarif)
            self.fields['border'].initial = self.check_none(price.border)
            self.fields['tarif2'].initial = self.check_none(price.tarif2)
            self.fields['border2'].initial = self.check_none(price.border2)
            self.fields['tarif3'].initial = self.check_none(price.tarif3)

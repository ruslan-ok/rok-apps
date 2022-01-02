from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, Select, NumberInput, UrlsInput
from task.const import APP_APART, NUM_ROLE_SERVICE
from task.models import Task
from apart.config import app_config
from apart.models import Price

role = 'price'

#----------------------------------
class CreateForm(BaseCreateForm):

    new_service = forms.ModelChoiceField(
        label=False,
        required=True,
        queryset=None,
        widget=Select(attrs={'label': _('service').capitalize(), 'class': 'col-md-3'}))

    class Meta:
        model = Task
        fields = ['new_service']

    def __init__(self, nav_item, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.fields['new_service'].queryset = Task.objects.filter(user=nav_item.user.id, app_apart=NUM_ROLE_SERVICE, task_1=nav_item.id)
        
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
        price_task = kwargs['instance']
        apart = Task.get_active_nav_item(price_task.user.id, APP_APART)
        self.fields['service'].queryset = Task.objects.filter(user=price_task.user.id, app_apart=NUM_ROLE_SERVICE, task_1=apart)
        self.fields['service'].initial = price_task.task_2
        if Price.objects.filter(task=price_task.id).exists():
            price = Price.objects.filter(task=price_task.id).get()
            self.fields['tarif'].initial = self.check_none(price.tarif)
            self.fields['border'].initial = self.check_none(price.border)
            self.fields['tarif2'].initial = self.check_none(price.tarif2)
            self.fields['border2'].initial = self.check_none(price.border2)
            self.fields['tarif3'].initial = self.check_none(price.tarif3)

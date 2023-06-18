from django import forms
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm, GroupForm
from rusel.widgets import DateInput, DateTimeInput, NumberInput, UrlsInput
from task.models import Task, Group
from apart.config import app_config

role = 'meter'

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
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Period')}))
    meter_el = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Electricity')}))
    meter_hw = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Hot water')}))
    meter_cw = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Cold water')}))
    meter_ga = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('Gas')}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    info = forms.CharField(
        label=_('Infofmation'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize': ''}))

    class Meta:
        model = Task
        fields = ['start', 'meter_el', 'meter_hw', 'meter_cw', 'meter_ga', 'info', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        apart = kwargs['instance'].task_1
        if (not apart.apart_has_el):
            self.fields['meter_el'].widget = HiddenInput()
        if (not apart.apart_has_hw):
            self.fields['meter_hw'].widget = HiddenInput()
        if (not apart.apart_has_cw):
            self.fields['meter_cw'].widget = HiddenInput()
        if (not apart.apart_has_gas):
            self.fields['meter_ga'].widget = HiddenInput()


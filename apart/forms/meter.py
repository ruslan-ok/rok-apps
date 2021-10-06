from django import forms
from django.forms.widgets import HiddenInput
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, DateTimeInput, NumberInput, UrlsInput
from task.models import Task
from apart.config import app_config
from apart.models import Apart, Meter

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
    period = forms.DateField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('period').capitalize()}))
    reading = forms.DateTimeField(
        label=False,
        required=True,
        widget=DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('meters reading date').capitalize()}))
    el = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('electricity').capitalize()}))
    hw = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('hot water').capitalize()}))
    cw = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('cold water').capitalize()}))
    ga = forms.IntegerField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('gas').capitalize()}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))

    class Meta:
        model = Task
        fields = ['period', 'reading', 'el', 'hw', 'cw', 'ga', 'info', 'url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        apart = Apart.objects.filter(user=kwargs['instance'].user.id, active=True).get()
        if Meter.objects.filter(task=kwargs['instance'].id).exists():
            meter = Meter.objects.filter(task=kwargs['instance'].id).get()
            self.fields['period'].initial = meter.period
            self.fields['reading'].initial = meter.reading
            self.fields['el'].initial = meter.el
            self.fields['hw'].initial = meter.hw
            self.fields['cw'].initial = meter.cw
            self.fields['ga'].initial = meter.ga
            if (not apart.has_el):
                self.fields['el'].widget = HiddenInput()
            if (not apart.has_hw):
                self.fields['hw'].widget = HiddenInput()
            if (not apart.has_cw):
                self.fields['cw'].widget = HiddenInput()
            if (not apart.has_gas):
                self.fields['ga'].widget = HiddenInput()

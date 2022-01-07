from django import forms
from django.utils.translation import gettext_lazy as _
from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateTimeInput, NumberInput
from task.const import ROLE_MARKER
from task.models import Task
from health.config import app_config

role = ROLE_MARKER

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    class Meta:
        model = Task
        fields = ['event', 'bio_height', 'bio_weight', 'bio_temp', 'bio_waist', 'bio_systolic', 'bio_diastolic', 'bio_pulse', 'info']

        widgets = {
            'event': DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('event date').capitalize(), 'type': 'datetime-local'}),
            'bio_height': NumberInput(attrs={'label':_('height, cm').capitalize(), 'step': '1'}),
            'bio_weight': NumberInput(attrs={'label':_('weight, kg').capitalize(), 'step': '0.1'}),
            'bio_temp': NumberInput(attrs={'label':_('temperature').capitalize(), 'step': '0.01'}),
            'bio_waist': NumberInput(attrs={'label':_('waist circumference').capitalize(), 'step': '1'}),
            'bio_systolic': NumberInput(attrs={'label':_('systolic blood pressure').capitalize(), 'step': '1'}),
            'bio_diastolic': NumberInput(attrs={'label':_('diastolic blood pressure').capitalize(), 'step': '1'}),
            'bio_pulse': NumberInput(attrs={'label':_('the number of heartbeats per minute').capitalize(), 'step': '1'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


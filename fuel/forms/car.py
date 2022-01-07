from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import ROLE_CAR
from fuel.config import app_config
from rusel.widgets import DateInput

role = ROLE_CAR

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    name = forms.CharField(
        label=_('model').capitalize(),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('car model').capitalize()}),
    )
    car_plate = forms.CharField(
        label=_('plate').capitalize(),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('car plate').capitalize()}),
    )
    start = forms.DateField(
        required=False,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('begin').capitalize(), 'placeholder': _('date of commencement of operation').capitalize()}),
    )
    stop = forms.DateField(
        required=False,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('end').capitalize(), 'placeholder': _('end date').capitalize()}),
    )
    info = forms.CharField(
        label=_('information').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
    )
    class Meta:
        model = Task
        fields = ['name', 'car_plate', 'start', 'stop', 'info']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        # value = kwargs['instance'].start.strftime('%Y-%m-%d')
        # self.fields['start'].initial = value


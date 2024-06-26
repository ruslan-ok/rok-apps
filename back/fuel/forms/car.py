from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import APP_FUEL
from core.widgets import DateInput, SwitchInput

app = APP_FUEL

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    name = forms.CharField(
        label=_('Model'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Car model')}),
    )
    car_plate = forms.CharField(
        label=_('Plate'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Car plate')}),
    )
    start = forms.DateField(
        required=False,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Begin'), 'placeholder': _('Date of commencement of operation')}),
    )
    stop = forms.DateField(
        required=False,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('End'), 'placeholder': _('End date')}),
    )
    car_notice = forms.BooleanField(
        label=False,
        required=False,
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Service Interval Notice')}),
    )
    info = forms.CharField(
        label=_('Information'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
    )
    class Meta:
        model = Task
        fields = ['name', 'car_plate', 'start', 'stop', 'info', 'car_notice']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)


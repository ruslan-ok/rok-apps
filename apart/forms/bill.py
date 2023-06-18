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
    bill_residents = forms.IntegerField(
        label=False,
        required=True,
        widget=NumberInput(attrs={'label': _('Number of residents'), 'step': '1'}))
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
        fields = ['start', 'event', 'info', 'url',]

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

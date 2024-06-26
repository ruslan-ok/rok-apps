from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from core.widgets import DateInput, UrlsInput
from apart.models import *
from task.const import APP_APART

app = APP_APART

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = PeriodMeters
        fields = ['start']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    start = forms.DateField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Period')}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    info = forms.CharField(
        label=_('Infofmation'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize': ''}))

    class Meta:
        model = PeriodMeters
        fields = ['start', 'info', 'url']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)


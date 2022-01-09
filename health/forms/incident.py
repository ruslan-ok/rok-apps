from django import forms
from django.utils.translation import gettext_lazy as _
from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import UrlsInput, CategoriesInput, DateInput
from task.const import ROLE_INCIDENT
from task.models import Task
from health.config import app_config

role = ROLE_INCIDENT

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))

    class Meta:
        model = Task
        fields = ['name', 'start', 'stop', 'diagnosis', 'info', 'url', 'categories', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start': DateInput(format='%Y-%m-%d', attrs={'label': _('start date of the incident').capitalize(), 'type': 'date'}),
            'stop': DateInput(format='%Y-%m-%d', attrs={'label': _('end date of the incident').capitalize(), 'type': 'date'}),
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

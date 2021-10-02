from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from apart.config import app_config

role = 'serv'

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
        label=_('title').capitalize(),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    info = forms.CharField(
        label=_('abbreviation').capitalize(),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Task
        fields = ['name', 'info']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

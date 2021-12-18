from django import forms
from django.utils.translation import gettext_lazy as _

from task.const import ROLE_MARKER
from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from health.config import app_config
from rusel.base.forms import GroupForm

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
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

#----------------------------------
class IncidentForm(GroupForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

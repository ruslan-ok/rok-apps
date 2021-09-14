from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task.base.forms import BaseCreateForm, BaseEditForm
from docs.config import app_config

#----------------------------------
class CreateForm(BaseCreateForm):
        
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'docs', *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):

    class Meta:
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'docs', *args, **kwargs)

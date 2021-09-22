from django import forms

from rusel.base.forms import BaseCreateForm, BaseEditForm
from docs.config import app_config

role = 'docs'

#----------------------------------
class CreateForm(BaseCreateForm):
        
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):

    class Meta:
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from todo.config import app_config

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'todo', *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):

    class Meta:
        model = Task
        fields = ['completed', 'name', 'important', 'add_step', 'in_my_day', 'remind', 'stop', 'repeat', 'repeat_num', 'repeat_days', 
                'categories', 'url', 'info', 'grp', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'stop': forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control date mb-3', 'type': 'date-local'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, 'todo', *args, **kwargs)

from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from apart.models import Apart
from rusel.widgets import SwitchInput
from apart.config import app_config

role = 'apart'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    has_gas = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('has gas').capitalize()}))
    has_ppo = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Has PPO')}))

    class Meta:
        model = Task
        fields = ['name', 'info', 'has_gas', 'has_ppo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        if Apart.objects.filter(task=kwargs['instance'].id).exists():
            apart = Apart.objects.filter(task=kwargs['instance'].id).get()
            self.fields['has_gas'].initial = apart.has_gas
            self.fields['has_ppo'].initial = apart.has_ppo

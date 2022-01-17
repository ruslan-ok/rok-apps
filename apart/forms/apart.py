from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
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
    name = forms.CharField(
        label=_('title').capitalize(),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    info = forms.CharField(
        label=_('address').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3'}))
    apart_has_el = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('has electricity').capitalize()}))
    apart_has_hw = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('has hot water').capitalize()}))
    apart_has_cw = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('has cold water').capitalize()}))
    apart_has_gas = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('has gas').capitalize()}))
    apart_has_tv = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Has Internet/TV')}))
    apart_has_phone = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Has phone')}))
    apart_has_zkx = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Has ZKX')}))
    apart_has_ppo = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Has PPO')}))

    class Meta:
        model = Task
        fields = ['name', 'info', 'apart_has_el', 'apart_has_hw', 'apart_has_cw', 'apart_has_gas', 'apart_has_tv', 'apart_has_phone', 'apart_has_zkx', 'apart_has_ppo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

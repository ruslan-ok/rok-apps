from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from cram.models import Lang
from apart.config import app_config

role = 'lang'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Lang
        fields = ['code']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    code = forms.CharField(
        label=_('Code'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Lang
        fields = ['code', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)



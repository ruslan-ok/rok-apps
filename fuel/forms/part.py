from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import ROLE_PART
from fuel.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput

role = ROLE_PART

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    part_chg_km = forms.CharField(
        label=_('Replacement interval, km'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    part_chg_mo = forms.CharField(
        label=_('Replacement interval, months'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))

    class Meta:
        model = Task
        fields = ['name', 'part_chg_km', 'part_chg_mo', 'info', 'url', 'categories', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


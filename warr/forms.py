from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import UrlsInput, CategoriesInput, DateInput
from task.models import Task
from task.const import ROLE_WARR
from warr.config import app_config

role = ROLE_WARR

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    start = forms.DateField(
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('warranty start date').capitalize(), 'type': 'date'}))
    grp = forms.ChoiceField(
        label=_('group').capitalize(),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),])
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))

    class Meta:
        model = Task
        fields = ['name', 'start', 'months', 'stop', 'info', 'grp', 'categories', 'url', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'months': forms.NumberInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


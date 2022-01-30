from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_EXPENSE
from expen.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput, SwitchInput
from rusel.base.forms import GroupForm

role = ROLE_EXPENSE

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
        label=_('operation').capitalize(),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add operation name').capitalize()}))
    grp = forms.ChoiceField(
        label=_('group').capitalize(),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),])
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))

    class Meta:
        model = Task
        fields = ['event', 'name', 'grp', 'expen_qty', 'expen_price', 'expen_rate', 'expen_rate_2', 'expen_usd', 'expen_eur', 'expen_kontr', 'info', 
        'url', 'categories', 'upload']
        widgets = {
            'event': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
            'expen_qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_rate_2': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_usd': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_eur': forms.NumberInput(attrs={'class': 'form-control'}),
            'expen_kontr': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

#----------------------------------
class ProjectForm(GroupForm):
    name = forms.CharField(
        label=_('project name').capitalize(),
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),)
    expen_byn = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in national currency').capitalize()}))
    expen_usd = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in dollars').capitalize()}))
    expen_eur = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in euro').capitalize()}))
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort', 'expen_byn', 'expen_usd', 'expen_eur']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

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
        fields = ['event', 'name', 'qty', 'price', 'rate', 'rate_2', 'usd', 'eur', 'kontr', 'info', 
        'url', 'categories', 'upload']
        widgets = {
            'event': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'rate_2': forms.NumberInput(attrs={'class': 'form-control'}),
            'usd': forms.NumberInput(attrs={'class': 'form-control'}),
            'eur': forms.NumberInput(attrs={'class': 'form-control'}),
            'kontr': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

#----------------------------------
class ExpenGroupForm(GroupForm):
    tot_byn = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in national currency').capitalize()}))
    tot_usd = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in dollars').capitalize()}))
    tot_eur = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('calculate totals in euro').capitalize()}))
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort', 'tot_byn', 'tot_usd', 'tot_eur']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

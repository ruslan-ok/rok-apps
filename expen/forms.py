from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_EXPENSE
from expen.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput, SwitchInput, DateInput, NegativeNumberInput
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
    event = forms.DateTimeField(
        required=True,
        widget=DateInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('Event date'), 'type': 'datetime-local'}))
    name = forms.CharField(
        label=_('Operation'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Add operation name')}))
    expen_qty = forms.DecimalField(
        label=_('Quantity'),
        required=False,
        widget=NegativeNumberInput(attrs={'step': '0.001'}))
    expen_price = forms.DecimalField(
        label=_('Price in NC'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    expen_rate_usd = forms.DecimalField(
        label=_('USD exchange rate'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}))
    expen_usd = forms.DecimalField(
        label=_('Amount in USD'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}))
    expen_rate_eur = forms.DecimalField(
        label=_('EUR exchange rate'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}))
    expen_eur = forms.DecimalField(
        label=_('Amount in EUR'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}))
    expen_rate_gbp = forms.DecimalField(
        label=_('GBP exchange rate'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}))
    expen_gbp = forms.DecimalField(
        label=_('Amount in GBP'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}))
    grp = forms.ChoiceField(
        label=_('Project'),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),])
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control', 'placeholder': _('Add link')}))
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control', 'placeholder': _('Add category')}))

    class Meta:
        model = Task
        fields = ['event', 'name', 'grp', 'expen_qty', 'expen_price', 'expen_rate_usd', 'expen_rate_eur', 'expen_rate_gbp', 'expen_usd', 'expen_eur', 'expen_gbp', 'expen_kontr', 'info', 
        'url', 'categories', 'upload']
        widgets = {
            'event': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
            'expen_kontr': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

#----------------------------------
class ProjectForm(GroupForm):
    name = forms.CharField(
        label=_('Project name'),
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),)
    expen_byn = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Calculate totals in national currency')}))
    expen_usd = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Calculate totals in dollars')}))
    expen_eur = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Calculate totals in euro')}))
    expen_gbp = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('Calculate totals in pounds')}))
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort', 'expen_byn', 'expen_usd', 'expen_eur', 'expen_gbp']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

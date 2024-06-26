from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_EXPENSE
from core.widgets import UrlsInput, CategoriesInput, DateInput, NegativeNumberInput
from core.forms import GroupForm

role = ROLE_EXPENSE

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)
        
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
        label=_('Price'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    price_unit = forms.CharField(
        label=_('Currency'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'onchange': 'afterCalendarChanged(0,0);'}))
    expen_rate_usd = forms.DecimalField(
        label=_('Exchange rate to USD'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00001'}))
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
        fields = ['event', 'name', 'grp', 'expen_qty', 'expen_price', 'price_unit', 'expen_rate_usd', 'expen_kontr', 'info', 
        'url', 'categories', 'upload']
        widgets = {
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
            'expen_kontr': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)

#----------------------------------
class ProjectForm(GroupForm):
    name = forms.CharField(
        label=_('Project name'),
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),)
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort', 'currency']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-2'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'currency': forms.TextInput(attrs={'class': 'form-control mb-2'}),
        }

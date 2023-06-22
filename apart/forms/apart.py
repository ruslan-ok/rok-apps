from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from apart.models import Apart
from apart.config import app_config

role = 'apart'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Apart
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    name = forms.CharField(
        label=_('Title'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    info = forms.CharField(
        label=_('Address'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize': ''}))
    sort = forms.CharField(
        label=_('Sort code'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    price_unit = forms.CharField(
        label=_('Default currency'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))
    bill_residents = forms.CharField(
        label=_('Number of residents'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'}))

    class Meta:
        model = Apart
        fields = ['name', 'info', 'sort', 'price_unit', 'bill_residents']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def clean_bill_residents(self):
        bill_residents = self.cleaned_data['bill_residents']
        if bill_residents == '':
            bill_residents = '0'
        return bill_residents


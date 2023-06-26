from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import ROLE_FUEL
from fuel.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput, DateInput

role = ROLE_FUEL

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
    car_odometr = forms.IntegerField(
        label=_('Odometer'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Odometer value')}))
    fuel_price = forms.DecimalField(
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
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))
    latitude = forms.HiddenInput()
    longitude = forms.HiddenInput()

    class Meta:
        model = Task
        fields = ['car_odometr', 'event', 'fuel_volume', 'fuel_price', 'info', 'url', 'categories', 'upload', 'latitude', 'longitude', 'price_unit', 'expen_rate_usd']
        widgets = {
            'fuel_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


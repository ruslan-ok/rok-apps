from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import ROLE_FUEL
from fuel.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput

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
    car_odometr = forms.IntegerField(
        label=_('Odometer'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Odometer value')}))
    fuel_price = forms.DecimalField(
        label=_('Price'),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
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
        fields = ['car_odometr', 'event', 'fuel_volume', 'fuel_price', 'info', 'url', 'categories', 'upload']
        widgets = {
            'event': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}),
            'fuel_volume': forms.NumberInput(attrs={'class': 'form-control'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


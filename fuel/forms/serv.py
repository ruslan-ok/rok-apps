from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task
from task.const import ROLE_SERVICE
from fuel.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput

role = ROLE_SERVICE

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
        label=_('odometer').capitalize(),
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3', 'placeholder': _('odometer value').capitalize()}))
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
        fields = ['car_odometr', 'info', 'url', 'categories', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms import BaseCreateForm, BaseEditForm
from core.widgets import UrlsInput, CategoriesInput, DateInput
from task.const import APP_HEALTH, ROLE_INCIDENT
from task.models import Task

app = APP_HEALTH
role = ROLE_INCIDENT

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    diagnosis = forms.CharField(
        label=_('Diagnosis'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
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
        fields = ['name', 'start', 'stop', 'diagnosis', 'info', 'url', 'categories', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start': DateInput(format='%Y-%m-%d', attrs={'label': _('Start date of the incident'), 'type': 'date'}),
            'stop': DateInput(format='%Y-%m-%d', attrs={'label': _('End date of the incident'), 'type': 'date'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)


from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from todo.config import app_config
from rusel.widgets import UrlsInput, CategoriesInput, CheckboxInput

role = 'todo'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    completed = forms.BooleanField(label=False, required=False, widget=CheckboxInput(attrs={'class': 'ms-1 mb-3', 'label': _('completed').capitalize()}))
    important = forms.BooleanField(label=False, required=False, widget=CheckboxInput(attrs={'class': 'ms-1 mb-3', 'label': _('important').capitalize()}))
    in_my_day = forms.BooleanField(label=False, required=False, widget=CheckboxInput(attrs={'class': 'ms-1 mb-3 me-3', 'label': _('in my day').capitalize()}))
    add_step = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': _('next step').capitalize()}), required=False)
    stop = forms.DateTimeField(
        label=_('termin').capitalize(),
        required=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime d-inline-block mb-3 me-3', 'type': 'datetime-local'}))
    grp = forms.ModelChoiceField(
        label=_('group').capitalize(),
        required=False,
        queryset=Group.objects.filter(role=role).order_by('sort'), 
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
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
        fields = ['completed', 'name', 'important', 'add_step', 'in_my_day', 'remind', 'stop', 'repeat', 'repeat_num', 'repeat_days', 
                'categories', 'url', 'info', 'grp', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'remind': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime d-inline-block mb-3 me-3', 'type': 'datetime-local'}),
            'repeat': forms.Select(attrs={'class': 'form-control mb-3'}),
            'repeat_num': forms.NumberInput(attrs={'class': 'form-control d-inline-block mb-3'}),
            'repeat_days': forms.NumberInput(attrs={'class': 'form-control d-inline-block mb-3'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def is_valid(self):
        """Return True if the form has no errors, or False otherwise."""
        return self.is_bound and not self.errors

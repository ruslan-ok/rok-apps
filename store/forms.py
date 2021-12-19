from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_STORE
from store.config import app_config
from store.models import Entry, Params
from rusel.widgets import UrlsInput, CategoriesInput, EntryUsernameInput, EntryValueInput

role = ROLE_STORE

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
        label=_('title').capitalize(),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(
        label=_('user name').capitalize(),
        required=False,
        widget=EntryUsernameInput(attrs={'class': ''}))
    value = forms.CharField(
        label=_('value').capitalize(),
        required=False,
        widget=EntryValueInput(attrs={'class': ''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))
    params = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    grp = forms.ModelChoiceField(
        label=_('group').capitalize(),
        required=False,
        queryset=Group.objects.filter(role=role).order_by('sort'), 
        widget=forms.Select(attrs={'class': 'form-control select mb-3'}))
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))

    class Meta:
        model = Task
        fields = ['name', 'username', 'value', 'params', 'info', 'grp', 'url', 'categories', 'upload']
        widgets = {
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        if Entry.objects.filter(task=self.instance, actual=1).exists():
            entry = Entry.objects.filter(task=self.instance, actual=1)[0]
            self.fields['username'].initial = entry.username
            self.fields['value'].initial = entry.value
            self.fields['params'].initial = entry.params
        else:
            self.fields['username'].initial = ''
            self.fields['value'].initial = ''
            self.fields['params'].initial = ''

#----------------------------------
class ParamsForm(BaseEditForm):

    class Meta:
        model = Params
        fields = ['ln', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

        

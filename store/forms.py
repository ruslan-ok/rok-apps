from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_STORE
from store.config import app_config
from store.models import Entry, Params
from rusel.widgets import UrlsInput, CategoriesInput, EntryUsernameInput, EntryValueInput, SwitchInput

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
    actual = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('actual').capitalize()}))
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
        fields = ['name', 'actual', 'username', 'value', 'params', 'info', 'grp', 'url', 'categories', 'upload']
        widgets = {
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        if Entry.objects.filter(task=self.instance, hist=None).exists():
            entry = Entry.objects.filter(task=self.instance, hist=None)[0]
            self.fields['username'].initial = entry.username
            self.fields['value'].initial = entry.value
            self.fields['params'].initial = entry.params
            self.fields['actual'].initial = (entry.actual == 1)
        else:
            self.fields['username'].initial = ''
            self.fields['value'].initial = ''
            self.fields['params'].initial = ''
            self.fields['actual'].initial = True

#----------------------------------
class ParamsForm(BaseEditForm):

    class Meta:
        model = Params
        fields = ['ln', 'un', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

        

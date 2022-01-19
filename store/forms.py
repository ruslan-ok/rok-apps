from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from rusel.base.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_STORE
from store.config import app_config
from store.models import Params
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
    store_username = forms.CharField(
        label=_('user name').capitalize(),
        required=False,
        widget=EntryUsernameInput(attrs={'class': ''}))
    store_value = forms.CharField(
        label=_('value').capitalize(),
        required=False,
        widget=EntryValueInput(attrs={'class': ''}))
    store_params = forms.IntegerField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    actual = forms.BooleanField(
        label=False, 
        required=False, 
        widget=SwitchInput(attrs={'class': 'ms-1 mb-3', 'label': _('actual').capitalize()}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))
    grp = forms.ChoiceField(
        label=_('group').capitalize(),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),]
    )
    categories = forms.CharField(
        label=_('categories').capitalize(),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add category').capitalize()}))

    class Meta:
        model = Task
        fields = ['name', 'store_username', 'store_value', 'store_params', 'actual', 'info', 'url', 'grp', 'categories', 'upload']
        widgets = {
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.fields['actual'].initial = not self.instance.completed
        if ('grp' in self.fields):
            self.fields['grp'].choices = self.get_groups_hier(self.instance.user.id, role)

    def get_groups_hier(self, user_id, role):
        groups = [(0, '----------'),]
        self.get_sorted_groups(groups, user_id, role)
        return groups

    def get_sorted_groups(self, groups, user_id, role, node=None, level=0):
        node_id = None
        if node:
            node_id = node.id
        items = Group.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
        for item in items:
            if (item.determinator != 'role') and (item.determinator != 'view'):
                groups.append((item.id, level * '—' + '  ' + item.name),)
                self.get_sorted_groups(groups, user_id, role, item, level+1)

    def clean_grp(self):
        ret = None
        grp_ok = self.cleaned_data['grp']
        if grp_ok:
            parent = Group.objects.filter(node=grp_ok)
            if (len(parent) > 0):
                raise  ValidationError(_('a group must not have subgroups').capitalize())
            ret = Group.objects.filter(id=grp_ok).get()
        return ret

#----------------------------------
class ParamsForm(BaseEditForm):

    class Meta:
        model = Params
        fields = ['ln', 'un', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']
        widgets = {
            'ln': forms.NumberInput(attrs={'class': 'form-control'}),
            'un': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

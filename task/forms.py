from django import forms
from django.utils.translation import gettext_lazy as _

from task.models import Group

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GroupForm(forms.ModelForm):
    is_leaf = forms.BooleanField(label=_('node is leaf'), disabled=True)
    level = forms.IntegerField(label=_('hierarchy level'), disabled=True)

    class Meta:
        model = Group
        fields = ['node', 'name', 'sort', 'is_leaf', 'level']

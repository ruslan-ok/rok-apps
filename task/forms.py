from django import forms
from django.utils.translation import gettext_lazy as _

from task.models import Group

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['node', 'name', 'sort']
        widgets = {
            'node': forms.Select(attrs={'class': 'form-control mb-5'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-5'}),
            'sort': forms.TextInput(attrs={'class': 'form-control mb-5'}),
        }

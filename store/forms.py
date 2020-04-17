from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Group, Entry, History, Params


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['code', 'name', 'uuid']

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['uuid'].widget.attrs['readonly'] = True

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'username', 'value', 'url', 'notes', 'uuid', 'group']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5}),
        }

class FilterForm(forms.ModelForm):
    class Meta:
        model = Params
        fields = ['group']

class ParamsForm(forms.ModelForm):
    ln = forms.IntegerField(label = _('length').capitalize(), min_value = 5, max_value = 100)
    class Meta:
        model = Params
        fields = ['ln', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']



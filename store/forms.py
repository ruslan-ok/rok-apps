from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Entry, Params


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'username', 'value', 'url', 'notes', 'uuid']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 5}),
        }

class ParamsForm(forms.ModelForm):
    ln = forms.IntegerField(label = _('length').capitalize(), min_value = 5, max_value = 100)
    class Meta:
        model = Params
        fields = ['ln', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']



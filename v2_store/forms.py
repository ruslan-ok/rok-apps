from django import forms
from django.utils.translation import gettext_lazy as _
from todo.models import Lst
from store.models import app_name, Entry, Params


class EntryForm(forms.ModelForm):
    category = forms.CharField(label = _('categories').capitalize(), widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)
    class Meta:
        model = Entry
        fields = ['title', 'username', 'value', 'url', 'notes', 'uuid', 'actual', 'params', 'lst']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'cols':10, 'placeholder': _('add note').capitalize(), 'data-autoresize': ''}),
        }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['lst'].queryset = Lst.objects.filter(user = user, app = app_name).order_by('name')

class ParamsForm(forms.ModelForm):
    ln = forms.IntegerField(label = _('length').capitalize(), min_value = 5, max_value = 100)
    class Meta:
        model = Params
        fields = ['ln', 'uc', 'lc', 'dg', 'sp', 'br', 'mi', 'ul', 'ac']



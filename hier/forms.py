from django import forms
from django.utils.translation import gettext_lazy as _
from .models import File
from .utils import STORAGE_TYPES


#----------------------------------
class FileForm(forms.ModelForm):
    storage = forms.ChoiceField(choices = STORAGE_TYPES)
    class Meta:
        model = File
        fields = ['name', 'code', 'notes', 'storage', 'icon', 'app']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 20}),
        }


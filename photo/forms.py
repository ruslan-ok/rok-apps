from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Photo


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['name', 'path', 'info']
        widgets = { 'name': forms.TextInput(attrs = {'readonly': 'readonly'}),
                    'path': forms.TextInput(attrs = {'readonly': 'readonly'}),
                    'info': forms.Textarea(attrs = { 'rows': 10, 'cols': 30, 'placeholder': _('add note').capitalize() }) }


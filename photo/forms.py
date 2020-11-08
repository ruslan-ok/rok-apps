from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Photo


class PhotoForm(forms.ModelForm):
    category = forms.CharField(label = _('categories').capitalize(), widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)
    class Meta:
        model = Photo
        fields = ['info']
        widgets = { 'info': forms.Textarea(attrs = { 'rows': 5, 'cols': 30, 'placeholder': _('add description').capitalize(), 'data-autoresize': '' }) }


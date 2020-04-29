from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Folder


#----------------------------------
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'code', 'icon', 'color', 'model_name']


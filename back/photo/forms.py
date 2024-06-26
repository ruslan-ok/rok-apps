from django import forms
from django.utils.translation import gettext_lazy as _

from task.const import ROLE_PHOTO
from photo.models import Photo

role = ROLE_PHOTO

class PhotoForm(forms.Form):
    class Meta:
        model = Photo
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

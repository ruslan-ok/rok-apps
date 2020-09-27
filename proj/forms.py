from django import forms
from hier.forms import DateInput
from .models import Direct, Proj
from django.utils.translation import gettext_lazy as _


#----------------------------------
class DirectForm(forms.ModelForm):
    class Meta:
        model = Direct
        fields = ['name', 'active']

#----------------------------------
class ProjForm(forms.ModelForm):
    class Meta:
        model = Proj
        fields = ['date', 'kol', 'price', 'course', 'usd', 'kontr', 'text']
        widgets = {
            'date': DateInput(),
            'text': forms.Textarea(attrs={'rows': 10, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }

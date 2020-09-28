from django import forms
from hier.forms import DateInput
from .models import Projects, Expenses
from django.utils.translation import gettext_lazy as _


#----------------------------------
class DirectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name', 'active']

#----------------------------------
class ProjForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['date', 'qty', 'price', 'rate', 'usd', 'kontr', 'text']
        widgets = {
            'date': DateInput(),
            'text': forms.Textarea(attrs={'rows': 10, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }

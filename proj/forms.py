from django import forms
from hier.forms import DateInput
from .models import Projects, Expenses
from django.utils.translation import gettext_lazy as _


#----------------------------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name']

#----------------------------------
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['date', 'qty', 'price', 'rate', 'usd', 'kontr', 'text']
        widgets = {
            'date': DateInput(attrs = {'onchange': 'AfterCalendarChanged(0,1)'}),
            'text': forms.Textarea(attrs={'rows': 10, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }

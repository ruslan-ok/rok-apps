from django import forms
from v2_hier.forms import DateInput
from proj.models import Projects, Expenses
from django.utils.translation import gettext_lazy as _


#----------------------------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ['name', 'tot_byn', 'tot_usd', 'tot_eur']

#----------------------------------
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = ['date', 'description', 'qty', 'price', 'rate', 'usd', 'rate_2', 'eur', 'kontr', 'text']
        widgets = {
            'date': DateInput(attrs = {'onchange': 'afterCalendarChanged(0,1)'}),
            'text': forms.Textarea(attrs={'rows': 10, 'cols': 30, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }

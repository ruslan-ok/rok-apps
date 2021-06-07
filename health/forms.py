from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime
from hier.forms import DateInput
from .models import app_name, Biomarker, Incident

#----------------------------------
class BiomarkerForm(forms.ModelForm):

    publ = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('when measurements were taken').capitalize(), required = True)

    class Meta:
        model = Biomarker
        exclude = ['user']
        widgets = { 'info': forms.Textarea(attrs={'rows': 10, 'cols': 30, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}), }

#----------------------------------
class IncidentForm(forms.ModelForm):

    class Meta:
        model = Incident
        exclude = ['user']
        widgets = {
            'beg': DateInput(attrs = {'onchange': 'afterCalendarChanged(0,1)'}),
            'end': DateInput(attrs = {'onchange': 'afterCalendarChanged(0,2)'}),
            'info': forms.Textarea(attrs={'rows': 10, 'cols': 30, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }



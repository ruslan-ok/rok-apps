from django import forms
from django.utils.translation import gettext_lazy as _
from apart.models import Apart

class ApartSelectForm(forms.Form):
    apart = forms.ModelChoiceField(
        label=_('apart').capitalize(),
        required=True,
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control select mb-3', 'onchange': 'apartChange(this)'}))

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apart'].queryset = Apart.objects.filter(user=user.id)
        if Apart.objects.filter(user=user.id, active=True).exists():
            self.fields['apart'].initial = Apart.objects.filter(user=user.id, active=True).get()

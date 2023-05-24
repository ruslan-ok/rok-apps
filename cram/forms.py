from django import forms
from django.utils.translation import gettext_lazy as _
from cram.models import Phrase
from task.const import ROLE_CRAM, ROLE_APP
from cram.config import app_config
from rusel.widgets import CategoriesInput

role = ROLE_CRAM
app = ROLE_APP[role]

class CreateForm(forms.ModelForm):

    class Meta:
        model = Phrase
        fields = ['user', 'grp']

    def __init__(self, config, role):
        super().__init__()
        self.config = config
        self.role = role
        
    def save(self, commit=True):
        ret = super().save(commit=False)
        ret.save()
        return ret


class EditForm(forms.ModelForm):
    grp = forms.ChoiceField(
        label=_('Group'),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),])
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))

    class Meta:
        model = Phrase
        fields = ['user', 'grp', 'categories']
        widgets = {
            'note': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self):
        super().__init__()
        self.config = app_config
        self.role = role



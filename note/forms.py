from django import forms
from .models import Note


#----------------------------------
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['name', 'code', 'descr', 'publ']
        widgets = {
            'descr': forms.Textarea(attrs={'rows': 20}),
        }

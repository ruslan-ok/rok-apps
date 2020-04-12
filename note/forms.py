from django import forms
from .models import List, Note, View


#----------------------------------
class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['name', 'code', 'color']


#----------------------------------
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['name', 'code', 'list', 'descr']
        widgets = {
            'descr': forms.Textarea(attrs={'rows': 20}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['list'].queryset = List.objects.filter(user = user.id).order_by('code', 'name')


#----------------------------------
class ViewForm(forms.ModelForm):
    class Meta:
        model = View
        fields = ['name', 'code']



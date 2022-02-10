from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime

from todo.models import Lst
from note.models import app_name, Note


#----------------------------------
class NoteForm(forms.ModelForm):
    publ = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('publication date').capitalize(), required = False)
    category = forms.CharField(label = _('categories').capitalize(), widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)
    class Meta:
        model = Note
        fields = ['name', 'descr', 'publ', 'url', 'lst']
        widgets = {
            'descr': forms.Textarea(attrs={'rows': 10, 'placeholder': _('add description').capitalize(), 'data-autoresize': ''}),
        }

    def __init__(self, user, app, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['lst'].queryset = Lst.objects.filter(user = user, app = app).order_by('name')

#----------------------------------
class FileForm(forms.Form):
    upload = forms.FileField()


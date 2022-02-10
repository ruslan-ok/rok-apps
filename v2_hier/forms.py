from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget #, AdminTimeWidget

from hier.models import Folder

#----------------------------------
class DateInput(AdminDateWidget):
    pass

class DateTimeInput(AdminSplitDateTime):
    pass

#----------------------------------
class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'code', 'icon', 'color', 'model_name']


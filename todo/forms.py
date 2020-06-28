from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Grp, Lst, Task, Step, TaskFiles

#----------------------------------
class GrpForm(forms.ModelForm):
    class Meta:
        model = Grp
        fields = ['name', 'node', 'sort']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['node'].queryset = Grp.objects.filter(user = user).order_by('name')

    def clean_node(self):
        node_ok = self.cleaned_data['node']
        if node_ok:
            inst_id = self.instance.id
            node_id = node_ok.id
            test = Grp.objects.filter(id = node_id).get()
            if (test.id == inst_id):
                raise  ValidationError(_('self reference'))
            
            while test.node:
                node_id = test.node.id
                test = Grp.objects.filter(id = node_id).get()
                if (test.id == inst_id):
                    raise  ValidationError(_('loop link'))

        return node_ok

#----------------------------------
class LstForm(forms.ModelForm):

    class Meta:
        model = Lst
        fields = ['name', 'grp', 'sort']

#----------------------------------
class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['name']

#----------------------------------
class TaskLstForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['lst']

#----------------------------------
class TaskInfoForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['info']
        widgets = {
          'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder':_('add note').capitalize()}),
        }
#----------------------------------
class StepForm(forms.ModelForm):

    class Meta:
        model = Step
        fields = ['name', 'sort']

#----------------------------------
class TaskFilesForm(forms.ModelForm):

    class Meta:
        model = TaskFiles
        fields = ['upload']


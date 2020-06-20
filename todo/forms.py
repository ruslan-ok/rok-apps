from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Grp, Lst, Task, Step

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
        #fields = ['name', 'in_my_day', 'start', 'reminder', 'repeat', 'completed', 'important']

#----------------------------------
class StepForm(forms.ModelForm):

    class Meta:
        model = Step
        fields = ['name', 'sort']


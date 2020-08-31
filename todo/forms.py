from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.contrib.admin.widgets import AdminSplitDateTime

from hier.forms import DateInput
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
class TaskNameForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['name']

#----------------------------------
class TaskForm(forms.ModelForm):
    remind = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('remind').capitalize(), required = False)
    url = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add link').capitalize()}), required = False)
    class Meta:
        model = Task
        fields = ['lst', 'stop', 'remind', 'repeat', 'repeat_num', 'repeat_days', 'info', 'url']
        widgets = {
            'stop': DateInput(),
            'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder':_('add note').capitalize(), 'data-autoresize':''}),
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




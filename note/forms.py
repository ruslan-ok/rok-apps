from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime, AdminDateWidget

from task.models import Group, Task, TaskGroup

app_name = 'note'

#----------------------------------
class NoteForm(forms.ModelForm):
    stop = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('publication date').capitalize(), required = False)
    lst = forms.ChoiceField(choices=[])
    url = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add link').capitalize()}), required = False)
    category = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add category').capitalize()}), required = False)
    cur_group = 0

    class Meta:
        model = Task
        fields = ['stop', 'name', 'lst', 'info', 'url', 'category']
        widgets = {
            'created': AdminDateWidget(),
            'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}),
        }

    def __init__(self, * args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.pop('instance')
        self.fields['lst'].choices = Group.get_tree(instance.user.id, app_name)
        if TaskGroup.objects.filter(task=instance.id, app=app_name).exists():
            self.cur_group = TaskGroup.objects.filter(task=instance.id, app=app_name).get().group.id
            self.initial['lst'] = self.cur_group


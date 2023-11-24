from django import forms
from task.models import Task
from task.const import NUM_ROLE_INCIDENT

class TempFilter(forms.Form):
    incident = forms.ChoiceField(label='Incident', choices=[])

    class Meta:
        fields = ['incident']

    def __init__(self):
        super().__init__()
        records = Task.objects.filter(app_health=NUM_ROLE_INCIDENT).order_by('-start')
        incidents = [(0, '----------')] + [(x.id, x.name) for x in records]
        self.fields['incident'].choices = incidents


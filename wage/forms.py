from django.forms import ModelForm
from .models import Params, Depart, Employee

class WageForm(ModelForm):
    class Meta:
        model = Params
        fields = ['user', 'period', 'employee']

class DepartForm(ModelForm):
    class Meta:
        model = Depart
        fields = ['user', 'name', 'sort']

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['user', 'fio', 'login', 'sort', 'email', 'passw', 'born', 'phone', 'addr', 'info']




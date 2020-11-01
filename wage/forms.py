from django import forms
from django.utils.translation import gettext_lazy as _
from hier.forms import DateInput
from .models import Period, Depart, DepHist, Post, Employee, FioHist, Child, Appoint, Education, EmplPer, PayTitle, Payment


class DepartForm(forms.ModelForm):
    class Meta:
        model = Depart
        fields = ['name', 'sort']

class DepHistForm(forms.ModelForm):
    
    class Meta:
        model = DepHist
        fields = ['dBeg', 'node']
        widgets = { 'dBeg': DateInput() }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['node'].queryset = Depart.objects.filter(user = user).order_by('name')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['name']

class PayTitleForm(forms.ModelForm):
    class Meta:
        model = PayTitle
        fields = ['name']

class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['planDays', 'DebtInRate', 'AvansDate', 'AvansRate', 'PaymentDate', 'PaymentRate', 'Part2Date', 'Part2Rate']
        widgets = { 'AvansDate':   DateInput(attrs = {'onchange': 'AfterCalendarChanged(0,1)'}),
                    'PaymentDate': DateInput(attrs = {'onchange': 'AfterCalendarChanged(0,2)'}),
                    'Part2Date':   DateInput(attrs = {'onchange': 'AfterCalendarChanged(0,3)'}) }

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        exclude = ['user', 'active']
        widgets = { 'born': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

class AppointForm(forms.ModelForm):
    class Meta:
        model = Appoint
        exclude = ['employee']
        widgets = { 'dBeg': DateInput(),
                    'dEnd': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['employee']
        widgets = { 'dBeg': DateInput(),
                    'dEnd': DateInput(),
                    'docdate': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

class FioHistForm(forms.ModelForm):
    class Meta:
        model = FioHist
        exclude = ['employee']
        widgets = { 'dEnd': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        exclude = ['employee']
        widgets = { 'born': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

class EmplPerForm(forms.ModelForm):
    class Meta:
        model = EmplPer
        exclude = ['employee', 'period']
        widgets = { 'dBeg': DateInput() }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['employee', 'period', 'direct']
        widgets = { 'payed': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }


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
        widgets = { 'AvansDate': DateInput(), 'PaymentDate': DateInput(), 'Part2Date': DateInput() }

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

"""
class EmplInfoForm(EmplPerForm):

    appoint_beg = forms.DateField(label = 'Назначение с', required = False)
    appoint_end = forms.DateField(label = 'Контракт до', required = False)
    salary = forms.DecimalField(label = 'Оклад', required = False, max_digits = 15, decimal_places = 0)
    currency = forms.CharField(label = 'Валюта оклада', required = False)
    department = forms.CharField(label = 'Отдел', required = False)
    post = forms.CharField(label = 'Должность', required = False)
    plan_days = forms.IntegerField(label = 'План, дней', required = False)
    accrued = forms.DecimalField(label = 'Начислено, BYN', required = False, max_digits = 15, decimal_places = 2)
    paid_out = forms.DecimalField(label = 'Выплачено, BYN', required = False, max_digits = 15, decimal_places = 2)
    debt_in_v = forms.DecimalField(label = 'Входящий остаток, USD', required = False, max_digits = 15, decimal_places = 2)
    accrued_v = forms.DecimalField(label = 'Начислено, USD', required = False, max_digits = 15, decimal_places = 2)
    paid_out_v = forms.DecimalField(label = 'Выплачено, USD', required = False, max_digits = 15, decimal_places = 2)
    debt_out_v = forms.DecimalField(label = 'Исходящий остаток, USD', required = False, max_digits = 15, decimal_places = 2)
    
    class Meta(EmplPerForm.Meta):
        fields = EmplPerForm.Meta.fields + ['appoint_beg', 'appoint_end', 'salary', 'currency', 'department', 'post', 'plan_days',
                                            'accrued', 'paid_out', 'debt_in_v', 'accrued_v', 'paid_out_v', 'debt_out_v']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Depart.objects.filter(user = user).order_by('name')
        self.fields['post'].queryset = Post.objects.filter(user = user).order_by('name')
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['appoint_beg'].widget.attrs['readonly'] = True
            self.fields['appoint_end'].widget.attrs['readonly'] = True
            self.fields['salary'].widget.attrs['readonly'] = True
            self.fields['currency'].widget.attrs['readonly'] = True
            self.fields['department'].widget.attrs['readonly'] = True
            self.fields['post'].widget.attrs['readonly'] = True
            self.fields['salaryRate'].widget.attrs['readonly'] = True
            self.fields['plan_days'].widget.attrs['readonly'] = True
            #self.fields['factDays'].widget.attrs['readonly'] = True
            self.fields['privilege'].widget.attrs['readonly'] = True
            self.fields['debtIn'].widget.attrs['readonly'] = True
            self.fields['accrued'].widget.attrs['readonly'] = True
            self.fields['paid_out'].widget.attrs['readonly'] = True
            self.fields['debtOut'].widget.attrs['readonly'] = True
            self.fields['debt_in_v'].widget.attrs['readonly'] = True
            self.fields['accrued_v'].widget.attrs['readonly'] = True
            self.fields['paid_out_v'].widget.attrs['readonly'] = True
            self.fields['debt_out_v'].widget.attrs['readonly'] = True
"""

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['employee', 'period', 'direct']
        widgets = { 'payed': DateInput(),
                    'info': forms.Textarea(attrs={'rows':3, 'cols':25, 'placeholder': _('add note').capitalize(), 'data-autoresize':''}) }

"""
class AccrualForm(PaymentForm):
    class Meta(PaymentForm.Meta):
        pass

class PayoutForm(PaymentForm):
    class Meta(PaymentForm.Meta):
        pass
"""


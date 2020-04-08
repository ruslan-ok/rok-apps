from django import forms
from .models import Period, Depart, DepHist, Post, Employee, FioHist, Child, Appoint, Education, EmplPer, PayTitle, Payment, Params


class WageForm(forms.ModelForm):
    class Meta:
        model = Params
        fields = ['period']

class DepartForm(forms.ModelForm):
    class Meta:
        model = Depart
        fields = ['name', 'sort']

class DepHistForm(forms.ModelForm):
    
    class Meta:
        model = DepHist
        fields = ['dBeg', 'node']

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
    dBeg = forms.DateField(label = 'Месяц/год', required = False, widget=forms.DateInput(format='%m.%Y'))
    
    class Meta:
        model = Period
        fields = ['dBeg', 'planDays', 'AvansDate', 'PaymentDate', 'AvansRate', 'PaymentRate', 'DebtInRate', 'Part2Date', 'Part2Rate']

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['fio', 'login', 'sort', 'email', 'passw', 'born', 'phone', 'addr', 'info']

class AppointForm(forms.ModelForm):
    class Meta:
        model = Appoint
        fields = ['tabnum', 'dBeg', 'dEnd', 'salary', 'currency', 'depart', 'post', 'taxded', 'info']

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['dBeg', 'dEnd', 'institution', 'course', 'specialty', 'qualification', 'document', 'number', 'city', 'docdate', 'info']

class FioHistForm(forms.ModelForm):
    class Meta:
        model = FioHist
        fields = ['dEnd', 'fio', 'info']

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['born', 'sort', 'name', 'info']

class EmplPerForm(forms.ModelForm):
    class Meta:
        model = EmplPer
        fields = ['employee', 'period', 'factDays', 'debtIn', 'debtOut', 'salaryRate', 'privilege', 'prevOut', 'dBeg']

class EmplInfoForm(EmplPerForm):

    fio = forms.CharField(label = 'ФИО', required = False)
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
        self.fields['employee'].queryset = Employee.objects.filter(user = user).order_by('fio')
        self.fields['department'].queryset = Depart.objects.filter(user = user).order_by('name')
        self.fields['post'].queryset = Post.objects.filter(user = user).order_by('name')
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['fio'].widget.attrs['readonly'] = True
            self.fields['appoint_beg'].widget.attrs['readonly'] = True
            self.fields['appoint_end'].widget.attrs['readonly'] = True
            self.fields['salary'].widget.attrs['readonly'] = True
            self.fields['currency'].widget.attrs['readonly'] = True
            self.fields['department'].widget.attrs['readonly'] = True
            self.fields['post'].widget.attrs['readonly'] = True
            self.fields['salaryRate'].widget.attrs['readonly'] = True
            self.fields['plan_days'].widget.attrs['readonly'] = True
            self.fields['factDays'].widget.attrs['readonly'] = True
            self.fields['privilege'].widget.attrs['readonly'] = True
            self.fields['debtIn'].widget.attrs['readonly'] = True
            self.fields['accrued'].widget.attrs['readonly'] = True
            self.fields['paid_out'].widget.attrs['readonly'] = True
            self.fields['debtOut'].widget.attrs['readonly'] = True
            self.fields['debt_in_v'].widget.attrs['readonly'] = True
            self.fields['accrued_v'].widget.attrs['readonly'] = True
            self.fields['paid_out_v'].widget.attrs['readonly'] = True
            self.fields['debt_out_v'].widget.attrs['readonly'] = True

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payed', 'sort', 'title', 'value', 'currency', 'rate', 'info']

class AccrualForm(PaymentForm):
    class Meta(PaymentForm.Meta):
        pass

class PayoutForm(PaymentForm):
    class Meta(PaymentForm.Meta):
        pass


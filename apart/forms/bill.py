from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import DateInput, NumberInput, UrlsInput
from task.models import Task
from apart.config import app_config
from apart.models import Bill

role = 'bill'

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    period = forms.DateField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('period').capitalize(), 'type': 'date'}))
    payment = forms.DateTimeField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%dT%H:%M', attrs={'label': _('date of payment').capitalize(), 'type': 'datetime-local'}))
    rate = forms.DecimalField(
        label=False,
        required=False,
        widget=NumberInput(attrs={'label': _('US dollar exchange rate')}))
    el_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    tv_bill = forms.DecimalField(label=False, required=False, widget=NumberInput())
    tv_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    phone_bill = forms.DecimalField(label=False, required=False, widget=NumberInput())
    phone_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    zhirovka = forms.DecimalField(label=False, required=False, widget=NumberInput())
    hot_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    repair_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    ZKX_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    water_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    gas_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    PoO = forms.DecimalField(label=False, required=False, widget=NumberInput())
    PoO_pay = forms.DecimalField(label=False, required=False, widget=NumberInput())
    info = forms.CharField(
        label=_('comment').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'label': _('comment').capitalize(), 'class': 'form-control mb-1', 'data-autoresize':''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('add link').capitalize()}))

    class Meta:
        model = Task
        fields = ['period', 'payment', 'rate', 'el_pay', 'tv_bill', 'tv_pay', 'phone_bill', 'phone_pay', 'zhirovka', 'hot_pay',
                    'repair_pay', 'ZKX_pay', 'water_pay', 'gas_pay', 'PoO', 'PoO_pay', 'info', 'upload', 'url']

    def check_none(self, value):
        if value:
            return value
        return 0

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        if Bill.objects.filter(task=kwargs['instance'].id).exists():
            bill = Bill.objects.filter(task=kwargs['instance'].id).get()
            self.fields['period'].initial = bill.period
            self.fields['payment'].initial = bill.payment
            self.fields['rate'].initial = self.check_none(bill.rate)
            self.fields['el_pay'].initial = self.check_none(bill.el_pay)
            self.fields['tv_bill'].initial = self.check_none(bill.tv_bill)
            self.fields['tv_pay'].initial = self.check_none(bill.tv_pay)
            self.fields['phone_bill'].initial = self.check_none(bill.phone_bill)
            self.fields['phone_pay'].initial = self.check_none(bill.phone_pay)
            self.fields['zhirovka'].initial = self.check_none(bill.zhirovka)
            self.fields['hot_pay'].initial = self.check_none(bill.hot_pay)
            self.fields['repair_pay'].initial = self.check_none(bill.repair_pay)
            self.fields['ZKX_pay'].initial = self.check_none(bill.ZKX_pay)
            self.fields['water_pay'].initial = self.check_none(bill.water_pay)
            self.fields['gas_pay'].initial = self.check_none(bill.gas_pay)
            self.fields['PoO'].initial = self.check_none(bill.PoO)
            self.fields['PoO_pay'].initial = self.check_none(bill.PoO_pay)

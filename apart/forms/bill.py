from django import forms
from django.utils.translation import gettext_lazy as _

from rusel.base.forms import BaseCreateForm, BaseEditForm
from rusel.widgets import MyNumberInput
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
        label=_('period').capitalize(),
        required=True,
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control date d-inline-block mb-1 me-3', 'type': 'date'}))
    payment = forms.DateTimeField(
        label=_('date of payment').capitalize(),
        required=True,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime d-inline-block mb-1 me-3', 'type': 'datetime-local'}))
    rate = forms.IntegerField(
        label=_('US dollar exchange rate'),
        required=False,
        widget=MyNumberInput(attrs={'class': ''}))
    el_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('electro - payment').capitalize(), 'class': ''}))
    tv_bill = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('Internet - accrued'), 'class': ''}))
    tv_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('TV - payment'), 'class': ''}))
    phone_bill = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('phone - accrued').capitalize(), 'class': ''}))
    phone_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('phone - payment').capitalize(), 'class': ''}))
    zhirovka = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('zhirovka').capitalize(), 'class': ''}))
    hot_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('heatenergy - payment').capitalize(), 'class': ''}))
    repair_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('overhaul - payment').capitalize(), 'class': ''}))
    ZKX_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('HCS - payment'), 'class': ''}))
    water_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('water - payment').capitalize(), 'class': ''}))
    gas_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('gas - payment').capitalize(), 'class': ''}))
    PoO = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('PoO - accrued'), 'class': ''}))
    PoO_pay = forms.DecimalField(required=False, widget=MyNumberInput(attrs={'label': _('PoO - payment'), 'class': ''}))
    info = forms.CharField(
        label=_('comment').capitalize(),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control mb-1'}))

    class Meta:
        model = Task
        fields = ['period', 'payment', 'rate', 'el_pay', 'tv_bill', 'tv_pay', 'phone_bill', 'phone_pay', 'zhirovka', 'hot_pay',
                    'repair_pay', 'ZKX_pay', 'water_pay', 'gas_pay', 'PoO', 'PoO_pay', 'info']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        if Bill.objects.filter(task=kwargs['instance'].id).exists():
            bill = Bill.objects.filter(task=kwargs['instance'].id).get()
            self.fields['period'].initial = bill.period
            self.fields['payment'].initial = bill.payment
            self.fields['rate'].initial = bill.rate
            self.fields['el_pay'].initial = bill.el_pay
            self.fields['tv_bill'].initial = bill.tv_bill
            self.fields['tv_pay'].initial = bill.tv_pay
            self.fields['phone_bill'].initial = bill.phone_bill
            self.fields['phone_pay'].initial = bill.phone_pay
            self.fields['zhirovka'].initial = bill.zhirovka
            self.fields['hot_pay'].initial = bill.hot_pay
            self.fields['repair_pay'].initial = bill.repair_pay
            self.fields['ZKX_pay'].initial = bill.ZKX_pay
            self.fields['water_pay'].initial = bill.water_pay
            self.fields['gas_pay'].initial = bill.gas_pay
            self.fields['PoO'].initial = bill.PoO
            self.fields['PoO_pay'].initial = bill.PoO_pay

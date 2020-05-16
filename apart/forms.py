from django import forms

from .models import Apart, Meter, Bill, Price


#----------------------------------
class ApartForm(forms.ModelForm):
    class Meta:
        model = Apart
        fields = ['name', 'addr', 'active', 'has_gas']

#----------------------------------
class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        fields = ['period', 'reading', 'el', 'hw', 'cw', 'ga', 'info']

#----------------------------------
class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['period', 'payment', 'el_pay', 'tv_bill', 'tv_pay', 'phone_bill', 'phone_pay', 'zhirovka', 'hot_pay', 'repair_pay', 'ZKX_pay', 'water_pay', 'gas_pay', 'rate', 'info']
    
#----------------------------------
class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        fields = ['service', 'period', 'tarif', 'border', 'tarif2', 'border2', 'tarif3', 'info']


from rest_framework import serializers
from rest_framework.settings import api_settings
from apart.models import *

class ApartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Apart
        fields = ['url', 'name', 'sort', 'info', 'price_unit', 'bill_residents']

class ApartMeterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=200, allow_blank=False, source='name')
    dt_from = serializers.DateField(required=False, allow_null=True, source='start')
    dt_until = serializers.DateTimeField(required=False, allow_null=True, format=api_settings.DATE_FORMAT, input_formats=['%Y-%m-%d'], source='stop')
    value = serializers.DecimalField(required=False, allow_null=True, max_digits=15, decimal_places=3, source='meter_zkx')
    class Meta:
        model = ApartMeter
        fields = ['id', 'task_1', 'code', 'dt_from', 'dt_until', 'value', 'sort']

class ApartServiceSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=True, max_length=200, allow_blank=False, source='name')
    dt_from = serializers.DateField(required=False, allow_null=True, source='start')
    dt_until = serializers.DateTimeField(required=False, allow_null=True, format=api_settings.DATE_FORMAT, input_formats=['%Y-%m-%d'], source='stop')
    class Meta:
        model = ApartService
        fields = ['id', 'task_1', 'code', 'dt_from', 'dt_until', 'sort']

class PeriodMetersSerializer(serializers.ModelSerializer):
    period = serializers.DateField(required=True, allow_null=False, source='start')
    class Meta:
        model = PeriodMeters
        fields = ['id', 'task_1', 'period', 'info']

class MeterValueSerializer(serializers.ModelSerializer):
    period = serializers.DateField(required=True, allow_null=False, source='start')
    code = serializers.CharField(required=True, max_length=200, allow_blank=False, source='name')
    value = serializers.DecimalField(required=False, allow_null=True, max_digits=15, decimal_places=3, source='meter_zkx')
    class Meta:
        model = MeterValue
        fields = ['id', 'task_1', 'period', 'code', 'event', 'value']

class PeriodServicesSerializer(serializers.ModelSerializer):
    period = serializers.DateField(required=True, allow_null=False, source='start')
    class Meta:
        model = PeriodServices
        fields = ['id', 'task_1', 'task_2', 'task_3', 'period', 'info', 'bill_residents']

class ServiceAmountSerializer(serializers.ModelSerializer):
    period = serializers.DateField(required=True, allow_null=False, source='start')
    code = serializers.CharField(required=True, max_length=200, allow_blank=False, source='name')
    tariff = serializers.DecimalField(required=False, allow_null=True, max_digits=15, decimal_places=5, source='price_tarif')
    accrued = serializers.DecimalField(required=False, allow_null=True, max_digits=15, decimal_places=2, source='bill_tv_bill')
    payment = serializers.DecimalField(required=False, allow_null=True, max_digits=15, decimal_places=2, source='bill_tv_pay')

    class Meta:
        model = ServiceAmount
        fields = ['id', 'task_1', 'period', 'code', 'event', 'tariff', 'accrued', 'payment']


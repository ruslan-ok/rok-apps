from datetime import date, datetime
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from task.const import *
from task.models import Task, TaskRoleInfo
from apart.const import *

class Apart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'apart_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_APART, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    name = models.CharField('Apartment name', max_length=200, blank=False)
    sort = models.CharField('Sort code', max_length=50, blank=True)
    info = models.TextField('Information', blank=True, null=True)
    price_unit = models.CharField('Currency', max_length=100, blank=True, null=True)
    active = models.BooleanField('Is active navigation item', null=True)
    bill_residents = models.IntegerField('Number of residents', null=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.name

    def delete_linked_items(self):
        for x in PeriodMeters.objects.filter(user=self.user.id, app_apart=NUM_ROLE_METER, task_1=self.id):
            x.delete_linked_items()
        for x in PeriodServices.objects.filter(user=self.user.id, app_apart=NUM_ROLE_BILL, task_1=self.id):
            x.delete_linked_items()
        PeriodMeters.objects.filter(user=self.user.id, app_apart=NUM_ROLE_METER, task_1=self.id).delete()
        PeriodServices.objects.filter(user=self.user.id, app_apart=NUM_ROLE_BILL, task_1=self.id).delete()
        ApartPrice.objects.filter(user=self.user.id, app_apart=NUM_ROLE_PRICE, task_1=self.id).delete()

    def get_attach_path_v2(self):
        return APP_APART + '/' + self.name
    
    def role_info(self):
        info = []
        meters = ApartMeter.objects.filter(user=self.user.id, app_apart=NUM_ROLE_METER_PROP, task_1=self.id)
        services = ApartService.objects.filter(user=self.user.id, app_apart=NUM_ROLE_SERV_PROP, task_1=self.id)
        if len(meters):
            info.append({'text': 'Счётчики: ' + str(len(meters))})
        if len(services):
            info.append({'text': 'Услуги: ' + str(len(services))})
        TaskRoleInfo.actualize(self.user, self.id, ROLE_APART, info, self.get_attach_path_v2())


class ApartPrice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'apart_price_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_PRICE, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='apart_price_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    name = models.CharField('Price name', max_length=200, blank=False)
    start = models.DateField('Valid from', blank=True, null=True)
    price_service = models.IntegerField('service code', null=True)
    price_tarif = models.DecimalField('tariff 1', null=True, max_digits=15, decimal_places=5)
    price_border = models.DecimalField('border 1', null=True, max_digits=15, decimal_places=4)
    price_tarif2 = models.DecimalField('tariff 2', null=True, max_digits=15, decimal_places=5)
    price_border2 = models.DecimalField('border 2', null=True, max_digits=15, decimal_places=4)
    price_tarif3 = models.DecimalField('tariff 3', null=True, max_digits=15, decimal_places=5)
    price_unit = models.CharField('Resource unit', max_length=100, blank=True, null=True)
    info = models.TextField('Information', blank=True, null=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    @classmethod
    def add_item(cls, user, apart_task: Task, service_id: int):
        apart = Apart.objects.filter(id=apart_task.id).get()
        price = ApartPrice.objects.create(user=user, app_apart=NUM_ROLE_PRICE, task_1=apart, start=datetime.now(), price_service=service_id)
        price.set_name()
        task = Task.objects.filter(id=price.id).get()
        return task

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.name

    def get_price_name(self):
        if self.start and self.price_service:
            return self.start.strftime('%Y.%m.%d') + ' ' + apart_service_name_by_id(self.price_service)
        return ''

    def set_name(self):
        self.name = 'Тариф ' + self.get_price_name()
        self.save()

    def get_attach_path_v2(self):
        return APP_APART + '/' + self.task_1.name + '/price/' + apart_service_name_by_id(self.price_service) + '/' + self.start.strftime('%Y.%m.%d')
    
    def role_info(self):
        b1 = self.price_border
        if not b1:
            b1 = 0

        t1 = self.price_tarif
        if not t1:
            t1 = 0

        b2 = self.price_border2
        if not b2:
            b2 = 0

        t2 = self.price_tarif2
        if not t2:
            t2 = 0

        t3 = self.price_tarif3
        if not t3:
            t3 = 0

        p1 = ''
        p2 = ''
        p3 = ''

        if (b1 == 0):
            p1 = str(t1)
        else:
            p1 = '{:.3f} {} {:.0f} {}'.format(t1, _('until'), b1, self.price_unit if self.price_unit else '')
            if (b2 == 0):
                p2 = '{:.3f}'.format(t2)
            else:
                p2 = '{:.3f} {} {:.0f} {}'.format(t2, _('until'), b2, self.price_unit if self.price_unit else '')
                p3 = '{:.3f}'.format(t3)

        info = []
        if p1:
            info.append({'text': p1})
        if p2:
            info.append({'text': p2})
        if p3:
            info.append({'text': p3})

        TaskRoleInfo.actualize(self.user, self.id, ROLE_PRICE, info, self.get_attach_path_v2())

class ApartMeter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'apart_meter_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_METER_PROP, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='apart_meter_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    name = models.CharField('Resource code', max_length=200, blank=False)
    start = models.DateField('Date from', blank=True, null=True)
    stop = models.DateTimeField('Date until', blank=True, null=True)
    sort = models.CharField('Sort code', max_length=50, blank=True)
    meter_zkx = models.DecimalField('Initial meter value', null=True, max_digits=15, decimal_places=3)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        name = self.get_name()
        if self.start or self.stop:
            start = stop = ''
            if self.start:
                start = self.start.strftime('%Y-%m-%d')
            if self.stop:
                stop = self.stop.strftime('%Y-%m-%d')
            name = f'{name} [{start} - {stop}]'
        return type(self).__name__ + ': ' + name

    def get_code(self):
        return self.name
    
    def get_name(self):
        name = self.name
        if self.name in APART_METER.keys():
            name = APART_METER[self.name]
        return name
    
    def get_sort(self):
        if not self.sort:
            return ''
        return self.sort
    
    def get_apart(self):
        return self.task_1
    
    def get_initial_value(self):
        return self.meter_zkx

    def get_initial_value_str(self):
        value = self.get_initial_value()
        return decimal_to_str(value)

    def get_from(self):
        return self.start

    def get_until(self):
        return self.stop

    def correct_groups_qty(self, mode, group_id=None, role=None):
        task = Task.objects.filter(id=self.id).get()
        return task.correct_groups_qty(mode, group_id, role)

class ApartService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'apart_service_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_SERV_PROP, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='apart_service_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    name = models.CharField('Service code', max_length=200, blank=False)
    start = models.DateField('Date from', blank=True, null=True)
    stop = models.DateTimeField('Date until', blank=True, null=True)
    sort = models.CharField('Sort code', max_length=50, blank=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        name = self.get_name()
        if self.start or self.stop:
            start = stop = ''
            if self.start:
                start = self.start.strftime('%Y-%m-%d')
            if self.stop:
                stop = self.stop.strftime('%Y-%m-%d')
            name = f'{name} [{start} - {stop}]'
        return type(self).__name__ + ': ' + name

    def get_code(self):
        return self.name
    
    def get_name(self):
        name = self.name
        if self.name in APART_SERVICE.keys():
            name = APART_SERVICE[self.name][1]
        return name

    def get_apart(self):
        return self.task_1
    
    def get_from(self):
        return self.start

    def get_until(self):
        return self.stop

    def get_sort(self):
        if not self.sort:
            return ''
        return self.sort

class PeriodMeters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'period_meters_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_METER, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='period_meters_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    name = models.CharField('Period meters name', max_length=200, blank=False)
    start = models.DateField('Period', blank=True, null=True)
    info = models.TextField('Information', blank=True, null=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.name

    def set_name(self):
        self.name = 'Показания счетчиков ' + self.start.strftime('%b %Y')
        self.save()

    @classmethod
    def next_period(cls, last=None):
        if not last:
            y = datetime.now().year
            m = datetime.now().month
            if (m == 1):
                m = 12
                y = y - 1
            else:
                m = m - 1
        else:
            y = last.year
            m = last.month
            
            if (m == 12):
                y = y + 1
                m = 1
            else:
                m = m + 1

        return date(y, m, 1)

    @classmethod
    def add_item(cls, user, apart_task: Task):
        apart = Apart.objects.filter(id=apart_task.id).get()
        few = PeriodMeters.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('-start')[:3]
        if (len(few) == 0):
            period = cls.next_period()
            last = None
            dt_start = None
            for meter_prop in ApartMeter.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_PROP, task_1=apart.id):
                value = meter_prop.get_initial_value()
                if value and meter_prop.start:
                    if not dt_start:
                        dt_start = meter_prop.start
                    elif dt_start > meter_prop.start:
                        dt_start = meter_prop.start
            if dt_start:
                period = datetime(dt_start.year, dt_start.month, 1).date()
        else:
            last = few[0]
            period = cls.next_period(last.start)
        meter = PeriodMeters.objects.create(user=user, app_apart=NUM_ROLE_METER, task_1=apart, start=period)
        meter.set_name()
        future = cls.next_period(period)
        apart_meters = {}
        for meter_prop in ApartMeter.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_PROP, task_1=apart.id).exclude(start__gte=future).exclude(stop__lt=period):
            value = None
            if meter_prop.start and meter_prop.start >= period and meter_prop.start < future:
                value = meter_prop.get_initial_value()
            if meter_prop.name not in apart_meters:
                apart_meters[meter_prop.name] = {'value': value, 'sort': meter_prop.sort, 'from': meter_prop.start }
            else:
                if apart_meters[meter_prop.name]['from'] < meter_prop.start:
                    apart_meters[meter_prop.name]['from'] = meter_prop.start
                    if apart_meters[meter_prop.name]['value'] != value:
                        apart_meters[meter_prop.name]['value'] = value
                    if apart_meters[meter_prop.name]['sort'] < meter_prop.sort:
                        apart_meters[meter_prop.name]['sort'] = meter_prop.sort
        code_list = sorted(apart_meters.keys(), key=lambda x: apart_meters[x]['sort'])
        for code in code_list:
            value = apart_meters[code]['value']
            dt_from = apart_meters[code]['from']
            if not value:
                dt_from = None
                if last and MeterValue.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=apart.id, name=code, start=last.start).exists():
                    last_value = MeterValue.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=apart.id, name=code, start=last.start).get()
                    meter_values = MeterValue.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=apart.id, name=code).order_by('start')
                    if dt_from:
                        meter_values = meter_values.filter(event__gte=dt_from).order_by('start')
                    first_value = meter_values[0]
                    if last_value and first_value and last_value.event and first_value.event and last_value.meter_zkx and first_value.meter_zkx:
                        value = last_value.meter_zkx
                        d1 = last_value.event
                        d2 = first_value.event
                        months = (d1.year - d2.year) * 12 + d1.month - d2.month
                        if months and last_value.meter_zkx > first_value.meter_zkx:
                            value += round((last_value.meter_zkx - first_value.meter_zkx) / months)
                        else:
                            if PeriodServices.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id, start=last_value.start).exists():
                                tmp_svc = PeriodServices.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id, start=last_value.start).get()
                                if tmp_svc.task_2 and MeterValue.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=apart.id, name=code, start=tmp_svc.task_2.start).exists():
                                    prev_value = MeterValue.objects.filter(user=user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=apart.id, name=code, start=tmp_svc.task_2.start).get()
                                    if prev_value.meter_zkx and last_value.meter_zkx > prev_value.meter_zkx:
                                        value += round(last_value.meter_zkx - prev_value.meter_zkx)
            MeterValue.objects.create(user=user, app_apart=NUM_ROLE_METER_VALUE, task_1=apart, name=code, start=period, meter_zkx=value, event=dt_from, sort=apart_meters[code]['sort'])
        task = Task.objects.filter(id=meter.id).get()
        return task

    def get_meter_value(self, code):
        if MeterValue.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=self.task_1, start=self.start, name=code).exists():
            meter_value = MeterValue.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=self.task_1, start=self.start, name=code).get()
            return meter_value.get_value()
        return None

    def delete_linked_items(self):
        MeterValue.objects.filter(user=self.user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=self.task_1.id, start=self.start).delete()

    def get_attach_path_v2(self):
        return APP_APART + '/' + self.task_1.name + '/meter/' + str(self.start.year) + '/' + str(self.start.month).zfill(2)
    
    def role_info(self):
        info = []
        for meter in MeterValue.objects.filter(user=self.user.id, app_apart=NUM_ROLE_METER_VALUE, task_1=self.task_1.id, start=self.start).order_by('sort'):
            info.append({'text': '{}: {}'.format(meter.get_name(), meter.get_value_str())})
        TaskRoleInfo.actualize(self.user, self.id, ROLE_METER, info, self.get_attach_path_v2())

class MeterValue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'meter_value_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_METER_VALUE, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='meter_value_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    start = models.DateField('Period', blank=True, null=True)
    sort = models.CharField('Sort code', max_length=50, blank=True)
    name = models.CharField('Resource code', max_length=200, blank=False)
    event = models.DateTimeField('Date of meter reading', blank=True, null=True)
    meter_zkx = models.DecimalField('Meter value', null=True, max_digits=15, decimal_places=3)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.get_name()

    def get_period(self):
        if self.start:
            return self.start.strftime('%Y-%m')
        return ''
    
    def get_code(self):
        return self.name
    
    def get_name(self):
        if self.name in APART_METER.keys():
            return APART_METER[self.name]
        return self.name
    
    def get_sort(self):
        if not self.sort:
            return ''
        return self.sort
    
    def get_apart(self):
        return self.task_1
    
    def get_value(self):
        return self.meter_zkx

    def get_value_str(self):
        return decimal_to_str(self.meter_zkx)

class PeriodServices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'period_service_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_BILL, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='period_service_link', blank=False, null=False)
    task_2 = models.ForeignKey(PeriodMeters, on_delete=models.SET_NULL, verbose_name='Previous period metters', related_name='prev_meter', blank=True, null=True)
    task_3 = models.ForeignKey(PeriodMeters, on_delete=models.SET_NULL, verbose_name='Current period metters', related_name='curr_meter', blank=True, null=True)
    created = models.DateTimeField('Creation time', default=datetime.now)
    name = models.CharField('Period services name', max_length=200, blank=False)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    start = models.DateField('Period', blank=True, null=True)
    bill_residents = models.IntegerField('Number of residents', null=True)
    info = models.TextField('Information', blank=True, null=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.name

    def set_name(self):
        self.name = 'Платежи ' + self.start.strftime('%b %Y')
        self.save()

    @classmethod
    def add_item(cls, user, apart_task: Task):
        apart = Apart.objects.filter(id=apart_task.id).get()
        few_meters = PeriodMeters.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('start')[:3]
        if len(few_meters) < 2:
            return None, _('there are no meter readings').capitalize()
        if not PeriodServices.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).exists():
            # First bill
            prev = few_meters[0]
            curr = few_meters[1]
            period = curr.start
        else:
            last = PeriodServices.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).order_by('-start')[0]
            period = PeriodMeters.next_period(last.start)
            if not PeriodMeters.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).exists(): 
                return None, _('there are no meter readings for the next period').capitalize()
            prev = last.task_3
            curr = PeriodMeters.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).get()
        service = PeriodServices.objects.create(user=user, app_apart=NUM_ROLE_BILL, task_1=apart, task_2=prev, task_3=curr, start=period, bill_residents=apart.bill_residents)
        future = PeriodMeters.next_period(period)
        serv_list = {}
        for serv_prop in ApartService.objects.filter(user=user.id, app_apart=NUM_ROLE_SERV_PROP, task_1=apart.id).exclude(start__gte=future).exclude(stop__lt=period):
            if serv_prop.name not in serv_list:
                serv_list[serv_prop.name] = serv_prop.sort
            else:
                if serv_list[serv_prop.name] < serv_prop.sort:
                    serv_list[serv_prop.name] = serv_prop.sort
        for code, sort in serv_list.items():
            few_serv = ServiceAmount.objects.filter(user=user.id, app_apart=NUM_ROLE_SERV_VALUE, task_1=apart.id, name=code, start__lt=period).order_by('-start')[:5]
            tariff, accrued = service.get_tariff_accrued(code)
            if not tariff and not accrued:
                accrued = 0
                for serv_value in few_serv:
                    accrued += serv_value.get_accrued()
                if (len(few_serv) > 0):
                    accrued = round(accrued / len(few_serv), 2)
            ServiceAmount.objects.create(user=user, app_apart=NUM_ROLE_SERV_VALUE, task_1=apart, name=code, start=period, sort=sort, price_tarif=tariff, bill_tv_bill=accrued)
        task = Task.objects.filter(id=service.id).get()
        return task, ''

    def delete_linked_items(self):
        ServiceAmount.objects.filter(user=self.user.id, app_apart=NUM_ROLE_SERV_VALUE, task_1=self.task_1.id, start=self.start).delete()

    def get_tarif(self, code):
        ret = {
            't1': Decimal(0),
            'b1': 0,
            't2': Decimal(0),
            'b2': 0,
            't3': Decimal(0)
        }
        service_id = APART_SERVICE[code][0]
        tarifs = ApartPrice.objects.filter(user=self.user.id, app_apart=NUM_ROLE_PRICE, task_1=self.task_1.id, price_service=service_id, start__lte=self.start).order_by('-start')[:1]

        if (len(tarifs) > 0):
        
            if tarifs[0].price_tarif:
                ret['t1'] = tarifs[0].price_tarif
            else:
                ret['t1'] = 0
        
            if tarifs[0].price_border:
                ret['b1'] = tarifs[0].price_border
            else:
                ret['b1'] = 0
        
            if tarifs[0].price_tarif2:
                ret['t2'] = tarifs[0].price_tarif2
            else:
                ret['t2'] = 0
        
            if tarifs[0].price_border2:
                ret['b2'] = tarifs[0].price_border2
            else:
                ret['b2'] = 0
        
            if tarifs[0].price_tarif3:
                ret['t3'] = tarifs[0].price_tarif3
            else:
                ret['t3'] = 0
    
        return ret

    def check_none(self, value):
        if not value:
            return 0
        return value

    def get_consumption(self, meter_code: str):
        prev = self.task_2
        curr = self.task_3
        if (not prev) or (not curr):
            return 0
        prev_value = prev.get_meter_value(meter_code)
        curr_value = curr.get_meter_value(meter_code)
        return self.check_none(curr_value) - self.check_none(prev_value)

    def get_tariff_accrued(self, serv_code: str):
        tar = self.get_tarif(serv_code)
        consump = 0
        match serv_code:
            case 'el_supply': consump = self.get_consumption('el_meter')
            case 'gas_supply': consump = self.get_consumption('gas_meter')
            case 'water_supply': consump = self.get_consumption('hw_meter') + self.get_consumption('cw_meter')
            case 'sewerage': consump = self.get_consumption('hw_meter') + self.get_consumption('cw_meter')
        
        if (tar['b1'] == 0) or (consump <= tar['b1']):
            accrued = consump * tar['t1']
        else:
            i_sum = tar['b1'] * tar['t1']
            if (tar['b2'] == 0) or (consump <= tar['b2']):
                accrued = i_sum + (consump - tar['b1']) * tar['t2']
            else:
                accrued = i_sum + (tar['b2'] - tar['b1']) * tar['t2'] + (consump - tar['b2']) * tar['t3']
        tarif = 0
        if consump:
            tarif = accrued / consump
        return round(tarif, 5), round(accrued, 2)

    def get_attach_path_v2(self):
        return APP_APART + '/' + self.task_1.name + '/bill/' + str(self.start.year) + '/' + str(self.start.month).zfill(2)
    
    def role_info(self):
        total_accrued = total_paid = Decimal(0)
        for service in ServiceAmount.objects.filter(user=self.user.id, app_apart=NUM_ROLE_SERV_VALUE, task_1=self.task_1.id, start=self.start):
            total_accrued += service.get_accrued()
            total_paid += service.get_payment()
        info = []
        info.append({'text': '{}: {}'.format('Начислено', total_accrued) })
        info.append({'text': '{}: {}'.format('Оплачено', total_paid) })
        TaskRoleInfo.actualize(self.user, self.id, ROLE_BILL, info, self.get_attach_path_v2())

class ServiceAmount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User', related_name = 'service_value_user')
    app_apart = models.IntegerField('Role in application Communal', default=NUM_ROLE_SERV_VALUE, null=False)
    task_1 = models.ForeignKey(Apart, on_delete=models.CASCADE, verbose_name='Apartment link', related_name='service_value_link', blank=False, null=False)
    created = models.DateTimeField('Creation time', default=datetime.now)
    last_mod = models.DateTimeField('Last modification time', blank=True, auto_now=True)
    start = models.DateField('Period', blank=True, null=True)
    sort = models.CharField('Sort code', max_length=50, blank=True)
    name = models.CharField('Service code', max_length=200, blank=False)
    price_tarif = models.DecimalField('Tariff', null=True, max_digits=15, decimal_places=5)
    bill_tv_bill = models.DecimalField('Accrued', null=True, max_digits=15, decimal_places=2)
    bill_tv_pay = models.DecimalField('Payment amount', null=True, max_digits=15, decimal_places=2)
    event = models.DateTimeField('Date of payment', blank=True, null=True)

    class Meta:
        db_table = 'task_task'
        managed = False

    def __repr__(self) -> str:
        return type(self).__name__ + ': ' + self.get_name()

    def get_period(self):
        if self.start:
            return self.start.strftime('%Y-%m')
        return ''

    def get_code(self):
        return self.name
    
    def get_name(self):
        if self.name in APART_SERVICE.keys():
            return APART_SERVICE[self.name][1]
        return self.name
    
    def get_sort(self):
        if not self.sort:
            return ''
        return self.sort
    
    def get_apart(self):
        return self.task_1
    
    def get_tarif(self) -> Decimal:
        if not self.price_tarif:
            return Decimal(0)
        return self.price_tarif

    def get_accrued(self) -> Decimal:
        if not self.bill_tv_bill:
            return Decimal(0)
        return self.bill_tv_bill

    def get_payment(self) -> Decimal:
        if not self.bill_tv_pay:
            return Decimal(0)
        return self.bill_tv_pay
    
    def get_tarif_str(self) -> str:
        return decimal_to_str(self.price_tarif)

    def get_accrued_str(self) -> str:
        return decimal_to_str(self.bill_tv_bill)

    def get_payment_str(self) -> str:
        return decimal_to_str(self.bill_tv_pay)


def decimal_to_str(value: Decimal|None) -> str:
    if not value:
        return '0'
    normalized = value.normalize()
    sign, digits, exponent = normalized.as_tuple()
    if exponent > 0:
        return str(Decimal((sign, digits + (0,) * exponent, 0)))
    else:
        return str(normalized)

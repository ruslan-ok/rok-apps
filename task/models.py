import calendar, json
from urllib.parse import urlparse
import requests

from datetime import date, time, datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.urls import NoReverseMatch

from rest_framework.reverse import reverse

from task.const import *
from rusel.utils import nice_date

class Group(models.Model):
    """
    Task groups
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='task_group')
    app = models.CharField(_('app name'), max_length=50, blank=False, default=APP_TODO, null=True)
    role = models.CharField(_('role name'), max_length=50, blank=False, default=ROLE_TODO, null=True)
    node = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name=_('node'), blank=True, null=True)
    name = models.CharField(_('group name'), max_length=200, blank=False)
    sort = models.CharField(_('sort code'), max_length=50, blank=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    completed = models.BooleanField(_('display completed records'), null=True)
    theme = models.IntegerField(_('theme id'), blank=True, null=True)
    sub_groups = models.CharField(_('content items sub groups'), max_length=10000, blank=True, null=True)
    use_sub_groups = models.BooleanField(_('using content items sub groups'), null=True)
    determinator = models.CharField(_('group category: "group", "role" or "view"'), max_length=10, blank=True, null=True)
    view_id = models.CharField(_('view identificator for "role" and "view"'), max_length=50, blank=True, null=True)
    items_sort = models.CharField(_('items sorting orders'), max_length=500, blank=True)
    info = models.TextField(_('information').capitalize(), blank=True, null=True)
    src_id = models.IntegerField(_('ID in source table'), blank=True, null=True)
    act_items_qty = models.IntegerField(_('items in group'), blank=True, null=True)
    #------------- Expen --------------
    expen_byn = models.BooleanField(_('totals in BYN'), null=True)
    expen_usd = models.BooleanField(_('totals in USD'), null=True)
    expen_eur = models.BooleanField(_('totals in EUR'), null=True)

    class Meta:
        verbose_name=_('task group')
        verbose_name_plural = _('task groups')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '.' * self.level() + self.name

    def s_id(self):
        return str(self.id)
    
    def get_shifted_name(self):
        return '.'*self.level()*2 + self.name
    
    def edit_url(self):
        if (self.app == APP_ALL):
            return 'todo:group'
        return self.app + ':group'

    def level(self):
        ret = 0
        node = self.node
        while node:
            ret += 1
            node = node.node
        return ret

    def is_leaf(self):
        return not Group.objects.filter(node=self.id).exists()

    def toggle_sub_group(self, sub_group_id):
        sgs = json.loads(self.sub_groups)
        for sg in sgs:
            if (sg['id'] == int(sub_group_id)):
                sg['is_open'] = not sg['is_open']
        self.sub_groups = json.dumps(sgs)
        self.save()

    def set_theme(self, theme_id):
        self.theme = theme_id
        self.save()

    def set_sort(self, sort_id):
        if self.items_sort.replace('-', '') == sort_id:
            if self.items_sort.replace('-', '') == self.items_sort:
                self.items_sort = '-' + sort_id
            else:
                self.items_sort = sort_id
        else:
            self.items_sort = sort_id
        self.save()

    def reverse_sort(self):
        if not self.items_sort:
            return
        if self.items_sort.replace('-', '') == self.items_sort:
            self.items_sort = '-' + self.items_sort
        else:
            self.items_sort = self.items_sort[1:]
        self.save()

    def delete_sort(self):
        self.items_sort = ''
        self.save()

    def expen_what_totals(self):
        if (not self.expen_byn) and (not self.expen_usd) and (not self.expen_eur):
            return True, False, False
        return self.expen_byn, self.expen_usd, self.expen_eur

    def expen_get_totals(self):
        byn = 0
        usd = 0
        eur = 0
        in_byn, in_usd, in_eur = self.expen_what_totals()
        for exp in TaskGroup.objects.filter(group=self.id):
            if in_byn:
                byn += exp.task.expen_amount('BYN')
            if in_usd:
                usd += exp.task.expen_amount('USD')
            if in_eur:
                eur += exp.task.expen_amount('EUR')
        return byn, usd, eur

    def expen_summary(self):
        in_byn, in_usd, in_eur = self.expen_what_totals()
        byn, usd, eur = self.expen_get_totals()
        res = []
        if in_usd:
            res.append(currency_repr(usd, '$'))
        if in_eur:
            res.append(currency_repr(eur, '€'))
        if in_byn:
            res.append(currency_repr(byn, ' BYN'))
        return res

    def get_absolute_url(self):
        if not self.app:
            return '/'
        id = self.id
        try:
            url = reverse(self.app + ':' + self.role + '-item', args = [id])
            return url
        except NoReverseMatch:
            return '/'

    def check_items_qty(self):
        if (self.determinator == None) or (self.determinator == 'group'):
            tgs = TaskGroup.objects.filter(group=self.id)
            qnt = 0
            for tg in tgs:
                if not tg.task.completed:
                    qnt += 1
            if (self.act_items_qty != qnt):
                self.act_items_qty = qnt
                self.save()


class Task(models.Model):
    """
    An Entity that can be a Task or something else
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'task_user')
    name = models.CharField(_('name').capitalize(), max_length=200, blank=False)
    event = models.DateTimeField(_('event date').capitalize(), blank=True, null=True)
    start = models.DateField(_('start date').capitalize(), blank=True, null=True)
    stop = models.DateTimeField(_('termin').capitalize(), blank=True, null=True)
    completed = models.BooleanField(_('completed').capitalize(), default=False)
    completion = models.DateTimeField(_('completion time').capitalize(), blank=True, null=True)
    in_my_day = models.BooleanField(_('in my day').capitalize(), default=False)
    important = models.BooleanField(_('important').capitalize(), default=False)
    remind = models.DateTimeField(_('remind').capitalize(), blank=True, null=True)
    last_remind = models.DateTimeField(_('last remind').capitalize(), blank=True, null=True)
    repeat = models.IntegerField(_('repeat').capitalize(), blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    repeat_num = models.IntegerField(_('repeat num').capitalize(), blank=True, null=True)
    repeat_days = models.IntegerField(_('repeat days').capitalize(), blank=True, null=True)
    categories = models.TextField(_('categories').capitalize(), blank=True, null=True)
    info = models.TextField(_('information').capitalize(), blank=True, null=True)
    src_id = models.IntegerField(_('ID in source table'), blank=True, null=True)
    app_task = models.IntegerField('Role in application Task', choices=TASK_ROLE_CHOICE, default=NONE, null=True)
    app_note = models.IntegerField('Role in application Note', choices=NOTE_ROLE_CHOICE, default=NONE, null=True)
    app_news = models.IntegerField('Role in application News', choices=NEWS_ROLE_CHOICE, default=NONE, null=True)
    app_store = models.IntegerField('Role in application Store', choices=STORE_ROLE_CHOICE, default=NONE, null=True)
    app_doc = models.IntegerField('Role in application Document', choices=DOC_ROLE_CHOICE, default=NONE, null=True)
    app_warr = models.IntegerField('Role in application Warranty', choices=WARR_ROLE_CHOICE, default=NONE, null=True)
    app_expen = models.IntegerField('Role in application Expense', choices=EXPEN_ROLE_CHOICE, default=NONE, null=True)
    app_trip = models.IntegerField('Role in application Trip', choices=TRIP_ROLE_CHOICE, default=NONE, null=True)
    app_fuel = models.IntegerField('Role in application Fueling', choices=FUEL_ROLE_CHOICE, default=NONE, null=True)
    app_apart = models.IntegerField('Role in application Communal', choices=APART_ROLE_CHOICE, default=NONE, null=True)
    app_health = models.IntegerField('Role in application Health', choices=HEALTH_ROLE_CHOICE, default=NONE, null=True)
    app_work = models.IntegerField('Role in application Work', choices=WORK_ROLE_CHOICE, default=NONE, null=True)
    app_photo = models.IntegerField('Role in application Photo Bank', choices=PHOTO_ROLE_CHOICE, default=NONE, null=True)
    created = models.DateTimeField(_('creation time').capitalize(), default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time').capitalize(), blank=True, auto_now=True)
    groups = models.ManyToManyField(Group, through='TaskGroup')
    active = models.BooleanField(_('is active navigation item').capitalize(), null=True)
    task_1 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #1'), related_name='task_link_1', blank=True, null=True)
    task_2 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #2'), related_name='task_link_2', blank=True, null=True)
    task_3 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #3'), related_name='task_link_3', blank=True, null=True)
    item_attr = models.CharField(_('item attributes').capitalize(), max_length=2000, blank=True, null=True)
    #------------ Expenses ------------
    expen_qty = models.DecimalField(_('quantity').capitalize(), blank=True, null=True, max_digits=15, decimal_places=3)
    expen_price = models.DecimalField(_('Price in NC'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_rate = models.DecimalField(_('USD exchange rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    expen_rate_2 = models.DecimalField(_('EUR exchange rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    expen_usd = models.DecimalField(_('amount in USD'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_eur = models.DecimalField(_('amount in EUR'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_kontr = models.CharField(_('manufacturer').capitalize(), max_length=1000, blank=True, null=True)
    #------------ Person --------------
    pers_dative = models.CharField(_('dative'), max_length=500, null=True)
    #------------- Trip ---------------
    trip_days = models.IntegerField(_('days'), null=True)
    trip_oper = models.IntegerField(_('operation'), null=True)
    trip_price = models.DecimalField(_('price'), max_digits=15, decimal_places=2, null=True)
    #------------- Store --------------
    store_username = models.CharField(_('username'), max_length=150, blank=True, null=True)
    store_value = models.CharField(_('value'), max_length=128, null=True)
    store_uuid = models.CharField(_('UUID'), max_length=100, blank=True, null=True)
    store_params = models.IntegerField(_('generator parameters used'), null=True)
    store_hist = models.DateTimeField(_('when archived'), null=True)
    #------------- Apart --------------
    apart_has_el = models.BooleanField(_('has electricity'), null=True)
    apart_has_hw = models.BooleanField(_('has hot water'), null=True)
    apart_has_cw = models.BooleanField(_('has cold water'), null=True)
    apart_has_gas = models.BooleanField(_('has gas'), null=True)
    apart_has_ppo = models.BooleanField(_('payments to the partnership of owners'), null=True)
    apart_has_tv = models.BooleanField(_('has Internet/TV'), null=True)
    apart_has_phone = models.BooleanField(_('has phone'), null=True)
    apart_has_zkx = models.BooleanField(_('has ZKX'), null=True)
    #------------- Meter --------------
    meter_el = models.IntegerField(_('electricity'), null=True)
    meter_hw = models.IntegerField(_('hot water'), null=True)
    meter_cw = models.IntegerField(_('cold water'), null=True)
    meter_ga = models.IntegerField(_('gas'), null=True)
    meter_zkx = models.DecimalField('account amount', null=True, max_digits=15, decimal_places=2)
    #------------- Price --------------
    price_service = models.IntegerField(_('service code'), null=True)
    price_tarif = models.DecimalField(_('tariff 1'), null=True, max_digits=15, decimal_places=5)
    price_border = models.DecimalField(_('border 1'), null=True, max_digits=15, decimal_places=4)
    price_tarif2 = models.DecimalField(_('tariff 2'), null=True, max_digits=15, decimal_places=5)
    price_border2 = models.DecimalField(_('border 2'), null=True, max_digits=15, decimal_places=4)
    price_tarif3 = models.DecimalField(_('tariff 3'), null=True, max_digits=15, decimal_places=5)
    price_unit = models.CharField(_('unit'), max_length=100, blank=True, null=True)
    #------------- Bill ---------------
    bill_residents = models.IntegerField(_('number of residents'), null=True)
    bill_el_pay = models.DecimalField('electro - payment', null=True, max_digits=15, decimal_places=2)
    bill_tv_bill = models.DecimalField('tv - accrued', null=True, max_digits=15, decimal_places=2)
    bill_tv_pay = models.DecimalField('tv - payment', null=True, max_digits=15, decimal_places=2)
    bill_phone_bill = models.DecimalField('phone - accrued', null=True, max_digits=15, decimal_places=2)
    bill_phone_pay = models.DecimalField('phone - payment', null=True, max_digits=15, decimal_places=2)
    bill_zhirovka = models.DecimalField('zhirovka', null=True, max_digits=15, decimal_places=2)
    bill_hot_pay = models.DecimalField('heatenergy - payment', null=True, max_digits=15, decimal_places=2)
    bill_repair_pay = models.DecimalField('overhaul - payment', null=True, max_digits=15, decimal_places=2)
    bill_zkx_pay = models.DecimalField('housing and communal services - payment', null=True, max_digits=15, decimal_places=2)
    bill_water_pay = models.DecimalField('water - payment', null=True, max_digits=15, decimal_places=2)
    bill_gas_pay = models.DecimalField('gas - payment', null=True, max_digits=15, decimal_places=2)
    bill_rate = models.DecimalField('rate', null=True, max_digits=15, decimal_places=4)
    bill_poo = models.DecimalField('pay to the Partnersheep of Owners - accrued', null=True, max_digits=15, decimal_places=2)
    bill_poo_pay = models.DecimalField('pay to the Partnersheep of Owners - payment', null=True, max_digits=15, decimal_places=2)
    #-------------- Car ----------------
    car_plate  = models.CharField(_('car number'), max_length=100, null=True, blank=True)
    car_odometr = models.IntegerField(_('odometer'), null=True)
    #-------------- Fuel ---------------
    fuel_volume = models.DecimalField(_('volume'), null=True, max_digits=5, decimal_places=3)
    fuel_price = models.DecimalField(_('price'), null=True, max_digits=15, decimal_places=2)
    #-------------- Part ---------------
    part_chg_km = models.IntegerField(_('replacement interval, km'), null=True)
    part_chg_mo = models.IntegerField(_('replacement interval, months'), null=True)
    #-------------- Repl ---------------
    repl_manuf = models.CharField(_('manufacturer'), max_length=1000, null=True, blank=True)
    repl_part_num = models.CharField(_('catalog number'), max_length=100, null=True, blank=True)
    repl_descr = models.CharField(_('name'), max_length=1000, null=True, blank=True)
    #------------- Health --------------
    diagnosis = models.CharField(_('diagnosis'), max_length=1000, blank=True)
    bio_height = models.IntegerField(_('height, cm'), blank=True, null=True)
    bio_weight = models.DecimalField(_('weight, kg'), blank=True, null=True, max_digits=5, decimal_places=1)
    bio_temp = models.DecimalField(_('temperature'), blank=True, null=True, max_digits=4, decimal_places=1)
    bio_waist = models.IntegerField(_('waist circumference'), blank=True, null=True)
    bio_systolic = models.IntegerField(_('systolic blood pressure'), blank=True, null=True)
    bio_diastolic = models.IntegerField(_('diastolic blood pressure'), blank=True, null=True)
    bio_pulse = models.IntegerField(_('the number of heartbeats per minute'), blank=True, null=True)
    # -------------
    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return self.name

    @classmethod
    def use_name(cls, app, role):
        ret = True
        if (app == APP_APART):
            ret = (role != ROLE_METER) and (role != ROLE_PRICE) and (role != ROLE_BILL)
        if (app == APP_FUEL):
            ret = (role != ROLE_FUEL) and (role != ROLE_SERVICE)
        return ret
        
    @classmethod
    def get_nav_role(cls, app):
        nav_role = ''
        if (app == APP_APART):
            nav_role = ROLE_APART
        if (app == APP_FUEL):
            nav_role = ROLE_CAR
        return nav_role

    @classmethod
    def set_active_nav_item(cls, user_id, app, active_nav_item_id):
        nav_role = cls.get_nav_role(app)
        if (not nav_role or not active_nav_item_id):
            return
        nav_items = Task.get_role_tasks(user_id, app, nav_role)
        nav_items.update(active=False)
        nav_items.filter(id=active_nav_item_id).update(active=True)

    @classmethod
    def get_active_nav_item(cls, user_id, app):
        nav_role = cls.get_nav_role(app)
        if nav_role:
            nav_items = Task.get_role_tasks(user_id, app, nav_role)
            if nav_items.filter(active=True).exists():
                return nav_items.filter(active=True).order_by('name')[0]
            if (len(nav_items) > 0):
                return nav_items.order_by('name')[0]
        return None

    @classmethod
    def get_role_tasks(cls, user_id, app, role, nav_item=None):
        if user_id:
            data = Task.objects.filter(user=user_id)
        else:
            data = Task.objects.all()

        if nav_item:
            data = data.filter(task_1=nav_item.id)

        if (app != APP_ALL):
            role_id = ROLES_IDS[app][role]
            if (app == APP_TODO):
                data = data.filter(app_task=role_id)
            if (app == APP_NOTE):
                data = data.filter(app_note=role_id)
            if (app == APP_NEWS):
                data = data.filter(app_news=role_id)
            if (app == APP_STORE):
                data = data.filter(app_store=role_id)
            if (app == APP_DOCS):
                data = data.filter(app_doc=role_id)
            if (app == APP_WARR):
                data = data.filter(app_warr=role_id)
            if (app == APP_EXPEN):
                data = data.filter(app_expen=role_id)
            if (app == APP_TRIP):
                data = data.filter(app_trip=role_id)
            if (app == APP_FUEL):
                data = data.filter(app_fuel=role_id)
            if (app == APP_APART):
                data = data.filter(app_apart=role_id)
            if (app == APP_HEALTH):
                data = data.filter(app_health=role_id)
            if (app == APP_WORK):
                data = data.filter(app_work=role_id)
            if (app == APP_PHOTO):
                data = data.filter(app_photo=role_id)
        return data

    def set_item_attr(self, app, attr):
        if not self.item_attr:
            value = {}
        else:
            value = json.loads(self.item_attr)
        value[app] = attr
        self.item_attr = json.dumps(value)
        self.save()

    def get_item_attr(self):
        if self.item_attr:
            return json.loads(self.item_attr)
        return {}

    def get_roles(self):
        roles = []
        for app in ROLES_IDS:
            app_field = None
            if (app == APP_TODO):
                app_field = self.app_task
            elif (app == APP_NOTE):
                app_field = self.app_note
            elif (app == APP_NEWS):
                app_field = self.app_news
            elif (app == APP_STORE):
                app_field = self.app_store
            elif (app == APP_DOCS):
                app_field = self.app_doc
            elif (app == APP_WARR):
                app_field = self.app_warr
            elif (app == APP_EXPEN):
                app_field = self.app_expen
            elif (app == APP_TRIP):
                app_field = self.app_trip
            elif (app == APP_FUEL):
                app_field = self.app_fuel
            elif (app == APP_APART):
                app_field = self.app_apart
            elif (app == APP_HEALTH):
                app_field = self.app_health
            elif (app == APP_WORK):
                app_field = self.app_work
            elif (app == APP_PHOTO):
                app_field = self.app_photo
            if app_field:
                base_role = list(ROLES_IDS[app].values())[0]
                for role in ROLES_IDS[app]:
                    if (app_field == ROLES_IDS[app][role]):
                        url_role = None
                        if (role != ROLE_BY_NUM[base_role]):
                            url_role = role
                        icon = ROLE_ICON[role]
                        href = self.get_url_for_app(app, url_role)
                        roles.append({'icon': icon, 'href': href, 'name': role})
        return roles

    def get_absolute_url(self):
        roles = self.get_roles()
        if (len(roles) < 1):
            return '/'
        return roles[0]['href']

    def get_url_for_app(self, app, role):
        if not app:
            return '/'
        id = self.id
        try:
            if role:
                url = reverse(app + ':' + role + '-item', args = [id])
            else:
                url = reverse(app + ':item', args = [id])
            return url
        except NoReverseMatch:
            return '/'
    
    def toggle_completed(self):
        next = None
        if (not self.completed) and self.repeat:
            if not self.start:
                self.start = self.stop # For a repeating task, remember the deadline that is specified in the first iteration in order to use it to adjust the next steps
            next = self.next_iteration()
        self.completed = not self.completed
        if self.completed:
            if not self.stop:
                self.stop = datetime.now()
            self.completion = datetime.now()
        else:
            self.completion = None
        self.save()
        for tg in TaskGroup.objects.filter(task_id=self.id):
            if self.completed:
                tg.group.act_items_qty -= 1
            else:
                tg.group.act_items_qty += 1
            tg.group.save()
        if self.completed and next: # Completed a stage of a recurring task and set a deadline for the next iteration
            if not Task.objects.filter(user = self.user, name = self.name, completed = False).exists():
                Task.objects.create(user = self.user, name = self.name, start = self.start, stop = next, important = self.important, \
                    remind = self.next_remind_time(), repeat = self.repeat, repeat_num = self.repeat_num, \
                    repeat_days = self.repeat_days, categories = self.categories, info = self.info)

    def next_iteration(self):
        next = None

        if self.stop and self.repeat:
            if (self.repeat == DAILY):
                next = self.stop + timedelta(self.repeat_num)
            elif (self.repeat == WEEKLY):
                next = self.stop + timedelta(self.repeat_num * 7)
            elif (self.repeat == MONTHLY):
                next = add_months(self.stop, self.repeat_num)
                if self.start and (next.day != self.start.day):
                    # For tasks that are repeated on a monthly basis, the day of the next iteration must be adjusted so that it coincides with the day of the first iteration.
                    # Relevant for tasks with a due date at the end of the month.
                    d = next.day
                    m = next.month
                    y = next.year
                    last_day = calendar.monthrange(next.year, next.month)[1]
                    if (last_day < self.start.day):
                        d = last_day
                    else:
                        d = self.start.day
                    next = date(y, m, d)
            elif (self.repeat == ANNUALLY):
                d = self.stop.day
                m = self.stop.month
                y = self.stop.year
                y += self.repeat_num
                last_day = calendar.monthrange(y, m)[1]
                if (d > last_day): # 29.02.YYYY
                    d = last_day
                next = date(y, m, d)

        return next

    def b_expired(self):
        if self.completed:
            return False

        if self.stop:
            return (self.stop < datetime.now()) and ((self.stop.date() != date.today()) or (self.stop.hour != 0) or (self.stop.minute != 0))
        return False

    def task_actual(self):
        if self.completed:
            return False

        if self.stop:
            return (self.stop > datetime.now()) or ((self.stop.date() == date.today()) and (self.stop.hour == 0) and (self.stop.minute == 0))
        return False

    def termin_date(self):
        d = self.stop
        if not d:
            return _('set due date').capitalize()
        if self.b_expired():
            s = str(_('expired')).capitalize() + ', '
        else:
            s = str(_('termin')).capitalize() + ': '
        return s + str(nice_date(d))
            
    def termin_time(self):
        if not self.stop:
            return ''
        if (self.stop.time() == time.min):
            return ''
        return self.stop.strftime('%H:%M')
    
    def remind_active(self):
        return self.remind and (not self.completed) and (self.remind > datetime.now())
    
    def remind_date(self):
        if self.remind:
            return nice_date(self.remind.date())
        return _('to remind').capitalize()
    
    def remind_time(self):
        if self.remind:
            return _('remind at').capitalize() + ' ' + self.remind.strftime('%H:%M')
        return ''
    
    def s_termin(self):
        d = self.stop

        if not d:
            return ''

        if self.b_expired():
            s = str(_('expired')).capitalize() + ', '
        else:
            s = str(_('termin')).capitalize() + ': '
        return s + str(nice_date(d))
            
    def s_repeat(self):
        if (not self.repeat) or (self.repeat == NONE):
            return ''
        if (self.repeat_num == 1):
            if (self.repeat == WORKDAYS):
                return REPEAT[WEEKLY][1].capitalize()
            return REPEAT[self.repeat][1].capitalize()
        
        rn = ''
        if self.repeat:
            rn = REPEAT_NAME[self.repeat]
        return '{} {} {}'.format(_('once every').capitalize(), self.repeat_num, rn)
    
    def repeat_s_days(self):
        if (self.repeat == WEEKLY):
            if (self.repeat_days == 0):
                return self.stop.strftime('%a')
            if (self.repeat_days == 1+2+4+8+16):
                return str(_('work days')).capitalize()
            ret = ''
            monday = datetime(2020, 7, 6, 0, 0)
            for i in range(7):
                if (self.repeat_days & (1 << i)):
                    if (ret != ''):
                        ret += ', '
                    ret += (monday +timedelta(i)).strftime('%a')
            return ret
        return ''
    
    def repeat_title(self):
        if (not self.repeat) or (self.repeat == NONE):
            return _('repeat').capitalize()
        if (self.repeat_num == 1):
            if (self.repeat == WORKDAYS):
                return REPEAT[WEEKLY][1].capitalize()
            return REPEAT[self.repeat][1].capitalize()
        
        rn = ''
        if self.repeat:
            rn = REPEAT_NAME[self.repeat]
        return '{} {} {}'.format(_('once every').capitalize(), self.repeat_num, rn)
    
    def repeat_info(self):
        if (self.repeat == WEEKLY):
            if (self.repeat_days == 0):
                return self.stop.strftime('%A')
            if (self.repeat_days == 1+2+4+8+16):
                return str(_('work days')).capitalize()
            ret = ''
            monday = datetime(2020, 7, 6, 0, 0)
            for i in range(7):
                if (self.repeat_days & (1 << i)):
                    if (ret != ''):
                        ret += ', '
                    ret += (monday +timedelta(i)).strftime('%A')
            return ret
        return ''
    
    def next_remind_time(self):
        if ((not self.remind) and (not self.last_remind)) or (not self.stop):
            return None
        if self.remind:
            rmd = self.remind
        else:
            rmd = self.last_remind
        delta = self.stop.date() - rmd.date()
        next = self.next_iteration()
        if (not next):
            return None
        rd = next - delta
        return datetime(rd.year, rd.month, rd.day, rmd.hour, rmd.minute, rmd.second)

    def s_in_my_day(self):
        if self.in_my_day:
            return _('Added in "My day"')
        else:
            return _('Add in "My day"')

    def expen_amount(self, currency):
        byn = 0
        if self.expen_price:
            byn = self.expen_price
            if self.expen_qty:
                byn = self.expen_price * self.expen_qty

        if (currency == 'USD'):
            if self.expen_usd:
                return self.expen_usd
            if byn and self.expen_rate:
                return byn / self.expen_rate

        if (currency == 'EUR'):
            if self.expen_eur:
                return self.expen_eur
            if byn and self.expen_rate_2:
                return byn / self.expen_rate_2

        if (currency == 'BYN'):
            if self.expen_price:
                return byn

            if self.expen_usd and self.expen_rate:
                return self.expen_usd * self.expen_rate

            if self.expen_eur and self.expen_rate_2:
                return self.expen_eur * self.expen_rate_2

        return 0

    def expen_summary(self):
        if TaskGroup.objects.filter(task=self.id, role=ROLE_EXPENSE).exists():
            tg = TaskGroup.objects.filter(task=self.id, role=ROLE_EXPENSE).get()
            in_byn, in_usd, in_eur = tg.group.expen_what_totals()
        else:
            in_byn, in_usd, in_eur = True, False, False
        usd = eur = byn = None
        if in_usd:
            usd = self.expen_amount('USD')
        if in_eur:
            eur = self.expen_amount('EUR')
        if in_byn:
            byn = self.expen_amount('BYN')

        res = []
        if in_usd and usd:
            res.append(currency_repr(usd, '$'))
        if in_eur and eur:
            res.append(currency_repr(eur, '€'))
        if in_byn and self.event:
            if (self.event < datetime(2016, 6, 1)):
                res.append(currency_repr(byn, ' BYR'))
            else:
                res.append(currency_repr(byn, ' BYN'))
        return res
    
    def correct_groups_qty(self, mode, group_id=None, role=None):
        if (mode == GIQ_ADD_TASK) and Group.objects.filter(id=group_id).exists():
            group = Group.objects.filter(id=group_id).get()
            if (group.determinator == 'group') or (group.determinator == None):
                TaskGroup.objects.create(task=self, group=group, role=group.role)
                if not self.completed:
                    group.act_items_qty += 1
                    group.save()
                    return True
        if (mode == GIQ_DEL_TASK) and role:
            tgs = TaskGroup.objects.filter(task=self.id, role=role)
            if (len(tgs) == 1):
                group = tgs[0].group
                if (not self.completed) and (group.act_items_qty > 0):
                    group.act_items_qty -= 1
                    group.save()
                tgs[0].delete()
                return True
        return False

    def delete_linked_items(self):
        for tg in TaskGroup.objects.filter(task=self.id):
            self.correct_groups_qty(GIQ_DEL_TASK, tg.group.role)
        Step.objects.filter(task=self.id).delete()
        Urls.objects.filter(task=self.id).delete()


GIQ_ADD_TASK = 1 # Task created
GIQ_DEL_TASK = 2 # Task deleted

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return date(year, month, day)
    


class Step(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='task_step')
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('step task'))
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    name = models.CharField(_('step name'), max_length=200, blank=False)
    sort = models.CharField(_('sort code'), max_length=50, blank=True)
    completed = models.BooleanField(_('step is completed'), default=False)

    class Meta:
        verbose_name = _('step')
        verbose_name_plural = _('steps')

    def __str__(self):
        return self.name
    
    @classmethod
    def next_sort(cls, task_id):
        if not Step.objects.filter(task=task_id).exists():
            return '0'
        last = Step.objects.filter(task=task_id).order_by('-sort')[0]
        return str(int(last.sort) + 1).zfill(3)

class TaskGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name=_('group'), blank=True, null=True)
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('task'))
    role = models.CharField(_('role name'), max_length=50, blank=False, default='todo', null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)

class Urls(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_('task'), related_name = 'task_urlsr')
    num = models.IntegerField(_('sort number'), default=0, null=True)
    href = models.URLField(_('URL'), max_length=2000, null=True, blank=True)
    status = models.IntegerField(_('status'), default=0, null=True)
    hostname = models.CharField(_('hostname'), max_length=200, blank=True, null=True)
    title = models.CharField(_('page title'), max_length=200, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)

    def name(self):
        if (self.status == 0):
            parsed = urlparse(self.href)
            scheme = ''
            if (not parsed.scheme):
                scheme = 'https://'
            val = URLValidator()
            try:
                val(scheme + self.href)
            except ValidationError:
                self.status = -1
            if (self.status == 0):
                self.status = 1
                if scheme:
                    self.href = scheme + self.href
                parsed = urlparse(self.href)
                if (parsed.hostname):
                    self.status = 2
                    self.hostname = parsed.hostname
                    hearders = {'headers':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0'}
                    try:
                        n = requests.get(self.href, headers=hearders)
                    except:
                        self.status = -2
                    if (self.status > 0):
                        self.status = 3
                        al = n.text
                        self.title = al[al.find('<title>') + 7 : al.find('</title>')]
                        if self.title:
                            self.ststus = 4
            self.save()
        if (self.hostname and self.title):
            return self.hostname + ': ' + self.title
        if (self.hostname):
            return self.hostname
        if (self.title):
            return self.title
        return self.href

def currency_repr(value, currency):
    if (round(value, 2) % 1):
        return '{:,.2f}{}'.format(value, currency).replace(',', '`')
    return '{:,.0f}{}'.format(value, currency).replace(',', '`')




import calendar, json, requests
from collections import Counter
from datetime import date, time, datetime, timedelta
from decimal import Decimal
from functools import reduce
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import NoReverseMatch
from django.utils import formats
from django.utils.crypto import get_random_string
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from rest_framework.reverse import reverse

from task import const
from task.const import *
from core.utils import nice_date
from core.categories import CATEGORY_DESIGN
from core.files import get_files_list_by_path, get_files_list_by_path_v2
#from fuel.utils import get_rest
#from news.get_info import get_info as news_get_info
#from expen.get_info import get_info as expen_get_info
#from apart.const import apart_service_name_by_id


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
    services_visible = models.BooleanField(_('show service tasks'), null=True)
    determinator = models.CharField(_('group category: "group", "role" or "view"'), max_length=10, blank=True, null=True)
    view_id = models.CharField(_('view identificator for "role" and "view"'), max_length=50, blank=True, null=True)
    items_sort = models.CharField(_('items sorting orders'), max_length=500, blank=True)
    info = models.TextField(_('information'), blank=True, null=True)
    src_id = models.IntegerField(_('ID in source table'), blank=True, null=True)
    act_items_qty = models.IntegerField(_('items in group'), blank=True, null=True)
    #------------- Expen --------------
    expen_byn = models.BooleanField(_('totals in BYN'), null=True)
    expen_usd = models.BooleanField(_('totals in USD'), null=True)
    expen_eur = models.BooleanField(_('totals in EUR'), null=True)
    expen_gbp = models.BooleanField(_('totals in GBP'), null=True)
    currency = models.CharField(_('default currency'), max_length=10, blank=True)

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
        if not self.app or (self.app == APP_ALL) or (self.app == APP_HOME):
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
        if self.sub_groups:
            sgs = json.loads(self.sub_groups)
            for sg in sgs:
                if (sg['id'] == int(sub_group_id)):
                    sg['is_open'] = not sg['is_open']
            self.sub_groups = json.dumps(sgs)
            self.save()

    def set_theme(self, theme_id):
        self.theme = theme_id
        self.save()

    def dark_theme(self):
        if not self.theme:
            return False
        return (self.theme < 8) or (self.theme > 14)

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

    def expen_get_amounts(self) -> tuple[Counter, Decimal]:
        amount_usd = 0
        cnt = Counter()
        for exp in TaskGroup.objects.filter(group=self.id):
            if exp.task.expen_qty and exp.task.expen_price and exp.task.price_unit:
                currency = exp.task.price_unit
                amount = exp.task.expen_price * exp.task.expen_qty
                cnt[currency] += amount
                if currency == 'USD':
                    amount_usd += amount
                elif exp.task.expen_rate_usd:
                    amount_usd += amount / exp.task.expen_rate_usd
        return cnt, amount_usd

    def expen_summary(self):
        amounts, amount_usd = self.expen_get_amounts()

        res = []
        if len(amounts) > 0 or 'USD' not in amounts:
            for currency, value in amounts.items():
                res.append(currency_repr(value, currency))
        res.append(currency_repr(amount_usd, '$', 'bg-primary text-white'))
        return res

    def get_absolute_url(self):
        if not self.app or not self.role:
            return '/'
        try:
            url = reverse(self.app + ':' + self.role + '-item', args = [self.id])
            return url
        except NoReverseMatch:
            return '/'

    def check_items_qty(self):
        if (self.determinator == None) or (self.determinator == 'group'):
            tgs = TaskGroup.objects.filter(group=self.id)
            qnt = 0
            for tg in tgs:
                if not tg.task.completed or tg.role != ROLE_TODO:
                    qnt += 1
            if (self.act_items_qty != qnt):
                self.act_items_qty = qnt
                self.save()

def detect_group(user, app, determinator, view_id, name):
    group = None
    if (determinator == 'group'):
        if Group.objects.filter(user=user.id, app=app, id=int(view_id)).exists():
            group = Group.objects.filter(user=user.id, app=app, id=int(view_id)).get()
    if (determinator == 'role'):
        if Group.objects.filter(user=user.id, app=app, determinator='role', view_id=view_id).exists():
            group = Group.objects.filter(user=user.id, app=app, determinator='role', view_id=view_id).get()
    if (determinator == 'view'):
        if Group.objects.filter(user=user.id, app=app, determinator='view', view_id=view_id).exists():
            group = Group.objects.filter(user=user.id, app=app, determinator='view', view_id=view_id).get()
    if not group and (determinator != 'group'):
        group = Group.objects.create(
            user=user, 
            app=app, 
            determinator=determinator, 
            view_id=view_id,
            name=name,
            act_items_qty=0,
            use_sub_groups=True,)
    return group

class Task(models.Model):
    """
    An Entity that can be a Task or something else
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'task_user')
    name = models.CharField(_('Name'), max_length=200, blank=True, null=True)
    event = models.DateTimeField(_('Event date'), blank=True, null=True)
    start = models.DateField(_('Start date'), blank=True, null=True)
    stop = models.DateTimeField(_('Termin'), blank=True, null=True)
    completed = models.BooleanField(_('Completed'), default=False, null=True)
    completion = models.DateTimeField(_('Completion time'), blank=True, null=True)
    in_my_day = models.BooleanField(_('In My day'), default=False, null=True)
    important = models.BooleanField(_('Important'), default=False, null=True)
    remind = models.DateTimeField(_('Remind'), blank=True, null=True)
    first_remind = models.DateTimeField(_('First remind'), blank=True, null=True)
    last_remind = models.DateTimeField(_('Last remind'), blank=True, null=True)
    repeat = models.IntegerField(_('Repeat'), blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    repeat_num = models.IntegerField(_('Repeat num'), blank=True, null=True)
    repeat_days = models.IntegerField(_('Repeat days'), blank=True, null=True)
    categories = models.TextField(_('Categories'), blank=True, null=True)
    info = models.TextField(_('Information'), blank=True, null=True)
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
    created = models.DateTimeField(_('Creation time'), default=datetime.now)
    last_mod = models.DateTimeField(_('Last modification time'), blank=True, auto_now=True)
    groups = models.ManyToManyField(Group, through='TaskGroup')
    active = models.BooleanField(_('Is active navigation item'), null=True)
    task_1 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #1'), related_name='task_link_1', blank=True, null=True)
    task_2 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #2'), related_name='task_link_2', blank=True, null=True)
    task_3 = models.ForeignKey('self', on_delete=models.SET_NULL, verbose_name=_('linked task #3'), related_name='task_link_3', blank=True, null=True)
    item_attr = models.CharField(_('Item attributes'), max_length=2000, blank=True, null=True)
    sort = models.CharField(_('sort code'), max_length=50, blank=True, null=True)
    latitude = models.CharField('Latitude', max_length=15, blank=True, null=True)
    longitude = models.CharField('Longitude', max_length=15, blank=True, null=True)
    #------------ Expenses ------------
    expen_qty = models.DecimalField(_('Quantity'), blank=True, null=True, max_digits=15, decimal_places=3)
    expen_price = models.DecimalField(pgettext_lazy('Expen', 'Price'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_rate_usd = models.DecimalField(_('Exchange rate to USD'), blank=True, null=True, max_digits=15, decimal_places=5)
    expen_rate_eur = models.DecimalField(_('EUR exchange rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    expen_rate_gbp = models.DecimalField(_('GBP exchange rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    expen_usd = models.DecimalField(_('amount in USD'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_eur = models.DecimalField(_('amount in EUR'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_gbp = models.DecimalField(_('amount in GBP'), blank=True, null=True, max_digits=15, decimal_places=2)
    expen_kontr = models.CharField(_('Manufacturer'), max_length=1000, blank=True, null=True)
    #------------ Person --------------
    pers_dative = models.CharField(_('dative'), max_length=500, null=True)
    #------------- Trip ---------------
    trip_days = models.IntegerField(_('days'), null=True)
    trip_oper = models.IntegerField(_('operation'), null=True)
    trip_price = models.DecimalField(_('price'), max_digits=15, decimal_places=2, null=True)
    #------------- Store --------------
    store_username = models.CharField(_('username'), max_length=150, blank=True, null=True)
    store_value = models.CharField(_('value'), max_length=128, null=True)
    store_params = models.IntegerField(_('generator parameters used'), null=True)
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
    meter_zkx = models.DecimalField('account amount', null=True, max_digits=15, decimal_places=3)
    #------------- Price --------------
    price_service = models.IntegerField(_('service code'), null=True)
    price_tarif = models.DecimalField(_('tariff 1'), null=True, max_digits=15, decimal_places=5)
    price_border = models.DecimalField(_('border 1'), null=True, max_digits=15, decimal_places=4)
    price_tarif2 = models.DecimalField(_('tariff 2'), null=True, max_digits=15, decimal_places=5)
    price_border2 = models.DecimalField(_('border 2'), null=True, max_digits=15, decimal_places=4)
    price_tarif3 = models.DecimalField(_('tariff 3'), null=True, max_digits=15, decimal_places=5)
    price_unit = models.CharField(_('currency'), max_length=100, blank=True, null=True)
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
    car_notice = models.BooleanField(_('Service Interval Notice'), null=True, default=False)
    #-------------- Fuel ---------------
    fuel_volume = models.DecimalField(_('volume'), null=True, max_digits=5, decimal_places=3)
    fuel_price = models.DecimalField(_('price'), null=True, max_digits=15, decimal_places=2)
    fuel_warn = models.DateTimeField(_('Warning notice time'), null=True)
    fuel_expir = models.DateTimeField(_('Expiration notice time'), null=True)
    #-------------- Part ---------------
    part_chg_km = models.IntegerField(_('replacement interval, km'), null=True)
    part_chg_mo = models.IntegerField(_('replacement interval, months'), null=True)
    #-------------- Repl ---------------
    repl_manuf = models.CharField(_('manufacturer'), max_length=1000, null=True, blank=True)
    repl_part_num = models.CharField(_('catalog number'), max_length=100, null=True, blank=True)
    repl_descr = models.CharField(_('name'), max_length=1000, null=True, blank=True)
    #------------- Health --------------
    diagnosis = models.CharField(_('diagnosis'), max_length=1000, blank=True, null=True)
    bio_height = models.IntegerField(_('height, cm'), blank=True, null=True)
    bio_weight = models.DecimalField(_('weight, kg'), blank=True, null=True, max_digits=5, decimal_places=2)
    bio_temp = models.DecimalField(_('temperature'), blank=True, null=True, max_digits=4, decimal_places=1)
    bio_waist = models.IntegerField(_('waist circumference'), blank=True, null=True)
    bio_systolic = models.IntegerField(_('systolic blood pressure'), blank=True, null=True)
    bio_diastolic = models.IntegerField(_('diastolic blood pressure'), blank=True, null=True)
    bio_pulse = models.IntegerField(_('the number of heartbeats per minute'), blank=True, null=True)
    #------------- Warranty --------------
    months = models.IntegerField(_('warranty termin, months'), blank=True, null=True, default=12)
    # -------------
    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        if self.name:
            return self.name
        return '?'

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
            return None
        role_id = ROLES_IDS[app][nav_role]
        cur_active = None
        if (app == APP_APART) and Task.objects.filter(user=user_id, app_apart=role_id, active=True).exists():
            cur_active = Task.objects.filter(user=user_id, app_apart=role_id, active=True).get()
        if (app == APP_FUEL) and Task.objects.filter(user=user_id, app_fuel=role_id, active=True).exists():
            cur_active = Task.objects.filter(user=user_id, app_fuel=role_id, active=True).get()
        if not cur_active:
            return None
        if cur_active.id == active_nav_item_id:
            return cur_active
        cur_active.active = False
        cur_active.save()
        if Task.objects.filter(user=user_id, id=active_nav_item_id).exists():
            new_active = Task.objects.filter(user=user_id, id=active_nav_item_id).get()
            new_active.active = True
            new_active.save()
            return new_active
        return None

    @classmethod
    def get_active_nav_item(cls, user_id, app):
        nav_role = cls.get_nav_role(app)
        if not nav_role:
            return None
        role_id = ROLES_IDS[app][nav_role]
        cur_active = None
        if (app == APP_APART) and Task.objects.filter(user=user_id, app_apart=role_id, active=True).exists():
            cur_active = Task.objects.filter(user=user_id, app_apart=role_id, active=True).get()
        if (app == APP_FUEL) and Task.objects.filter(user=user_id, app_fuel=role_id, active=True).exists():
            cur_active = Task.objects.filter(user=user_id, app_fuel=role_id, active=True).get()
        return cur_active

    @classmethod
    def get_role_tasks(cls, user_id, app, role, nav_item=None):
        if user_id:
            data = TaskInfo.objects.filter(user_id=user_id)
        else:
            data = TaskInfo.objects.all()

        if data and nav_item:
            data = data.filter(task_1_id=nav_item.id)

        if data and (app != APP_ALL) and (app != APP_HOME):
            role_id = ROLES_IDS[app][role]
            data = data.filter(num_role=role_id)
        return data

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
                        roles.append({'icon': icon, 'href': href, 'name': role, 'name_mod': role.replace('expense', 'expen').replace('service', 'fuel')})
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
    
    def toggle_completed(self, do_complete=False):
        next = None
        if self.completed and do_complete:
            return None
        if (not self.completed) and self.repeat:
            if not self.start and self.stop:
                self.start = self.stop.date() # For a repeating task, remember the deadline that is specified in the first iteration in order to use it to adjust the next steps
            next = self.next_iteration()
        self.completed = not self.completed
        if self.completed:
            if not self.stop:
                self.stop = datetime.now()
            self.completion = datetime.now()
        else:
            self.completion = None
        if (self.app_news or self.app_expen) and not self.event:
            self.event = datetime.now()
        self.save()
        # if self.app_news:
        #     news_get_info(self)
        # if self.app_expen:
        #     expen_get_info(self)
        self.correct_groups_qty(GIQ_CMP_TASK, todo_only=True)
        next_task = None
        if self.completed and next: # Completed a stage of a recurring task and set a deadline for the next iteration
            if Task.objects.filter(user=self.user, app_task=self.app_task, name=self.name, completed=False).exists():
                next_task = Task.objects.filter(user=self.user, app_task=self.app_task, name=self.name, completed=False)[0]
            else:
                next_task = Task.objects.create(user=self.user, app_task=self.app_task, app_news=self.app_news, app_expen=self.app_expen, 
                    name=self.name, start=self.start, stop=next, important=self.important,
                    remind=self.next_remind_time(), repeat=self.repeat, repeat_num=self.repeat_num,
                    repeat_days=self.repeat_days, categories=self.categories, info=self.info)
                next_task.get_info(ROLE_TODO)
                # if next_task.app_news:
                #     news_get_info(next_task)
                # if next_task.app_expen:
                #     expen_get_info(next_task)
                if TaskGroup.objects.filter(task=self.id, role=ROLE_TODO).exists():
                    group = TaskGroup.objects.filter(task=self.id, role=ROLE_TODO).get().group
                    next_task.correct_groups_qty(GIQ_ADD_TASK, group.id)
                if TaskGroup.objects.filter(task=self.id, role=ROLE_NEWS).exists():
                    group = TaskGroup.objects.filter(task=self.id, role=ROLE_NEWS).get().group
                    next_task.correct_groups_qty(GIQ_ADD_TASK, group.id)
                if TaskGroup.objects.filter(task=self.id, role=ROLE_EXPENSE).exists():
                    group = TaskGroup.objects.filter(task=self.id, role=ROLE_EXPENSE).get().group
                    next_task.correct_groups_qty(GIQ_ADD_TASK, group.id)
        return next_task

    def get_attach_path(self, role):
        if role in ROLES_IDS.keys():
            app = role
            role = list(ROLES_IDS[app].keys())[0]
        else:
            app = ROLE_APP[role]
        ret = app + '/' + role + '_' + str(self.id)
        if (app == APP_APART):
            match (role, self.app_apart):
                case (const.ROLE_APART, const.NUM_ROLE_APART):
                    ret = APP_APART + '/' + self.name
                case (const.ROLE_PRICE, const.NUM_ROLE_PRICE):
                    ret = APP_APART + '/' + self.task_1.name + '/price/' + apart_service_name_by_id(self.price_service) + '/' + self.start.strftime('%Y.%m.%d')
                case (const.ROLE_METER, const.NUM_ROLE_METER):
                    ret = APP_APART + '/' + self.task_1.name + '/meter/' + str(self.start.year) + '/' + str(self.start.month).zfill(2)
                case (const.ROLE_BILL, const.NUM_ROLE_BILL):
                    ret = APP_APART + '/' + self.task_1.name + '/bill/' + str(self.start.year) + '/' + str(self.start.month).zfill(2)
        if (app == APP_FUEL):
            match (role, self.app_fuel):
                case (const.ROLE_CAR, const.NUM_ROLE_CAR):
                    ret = APP_FUEL + '/' + self.name + '/car'
                case (const.ROLE_PART, const.NUM_ROLE_PART):
                    ret = APP_FUEL + '/' + self.task_1.name + '/part/' + self.name
                case (const.ROLE_SERVICE, const.NUM_ROLE_SERVICE):
                    ret = APP_FUEL + '/' + self.task_1.name + '/service/' + self.task_2.name + '/' + self.event.strftime('%Y.%m.%d')
                case (const.ROLE_FUEL, const.NUM_ROLE_FUEL):
                    ret = APP_FUEL + '/' + self.task_1.name + '/fuel/' + self.event.strftime('%Y.%m.%d')
        if (app == APP_WARR):
            match (role, self.app_warr):
                case (const.ROLE_WARR, const.NUM_ROLE_WARR):
                    ret = APP_WARR + '/' + self.name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('«', '_').replace('<', '_').replace('>', '_').replace('|', '_')

        return f'{settings.DJANGO_STORAGE_PATH}/{self.user.username}/attachments/{ret}/'

    def get_files_list(self, role):
        fss_path = self.get_attach_path(role)
        return get_files_list_by_path(role, self.id, fss_path)

    def get_info(self, role=ROLE_TODO):
        attr = []
        if self.in_my_day:
            attr.append({'myday': True})

        step_total = 0
        step_completed = 0
        for step in Step.objects.filter(task=self.id):
            step_total += 1
            if step.completed:
                step_completed += 1
        if (step_total > 0):
            attr.append({'text': '{} {} {}'.format(step_completed, _('out of'), step_total)})

        if self.stop:
            attr.append({'termin': True})

        if (self.remind != None):
            attr.append({'icon': 'remind'})

        if self.completed:
            attr.append({'text': '{}: {}'.format(_('Completion'), self.completion.strftime('%d.%m.%Y') if self.completion else '')})

        self.actualize_role_info(ROLE_APP[role], role, attr)

    def days_to_next(self, repeat_last, repeat_days, repeat_num):
        from_dow = repeat_last.weekday()
        for day in range(from_dow + 1, 7):
            if repeat_days & 2**day:
                return day - from_dow
        for day in range(0, from_dow + 1):
            if repeat_days & 2**day:
                return day - from_dow + 7 * repeat_num
        return 7

    def next_iteration(self):
        next = None

        if self.stop and self.repeat:
            if (self.repeat == DAILY):
                next = self.stop + timedelta(self.repeat_num)
            elif (self.repeat == WEEKLY):
                after_days = self.days_to_next(self.stop, self.repeat_days, self.repeat_num)
                next = self.stop + timedelta(after_days)
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
            return _('Set due date')
        if self.b_expired():
            s = str(_('Expired')) + ', '
        else:
            s = str(_('Termin')) + ': '
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
        return _('To remind')
    
    def remind_time(self):
        if self.remind:
            return _('Remind at') + ' ' + self.remind.strftime('%H:%M')
        return ''
    
    def s_termin(self):
        d = self.stop

        if not d:
            return ''

        if self.b_expired():
            s = _('Expired') + ', '
        else:
            s = _('Termin') + ': '
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
        return '{} {} {}'.format(_('Once every'), self.repeat_num, rn)
    
    def repeat_s_days(self):
        if (self.repeat == WEEKLY):
            if (self.repeat_days == 0):
                return formats.date_format(self.stop if self.stop else self.start, 'D')
            if (self.repeat_days == 1+2+4+8+16):
                return str(_('Work days'))
            ret = ''
            monday = datetime(2020, 7, 6, 0, 0)
            for i in range(7):
                if (self.repeat_days & (1 << i)):
                    if (ret != ''):
                        ret += ', '
                    ret += formats.date_format(monday +timedelta(i), 'D')
            return ret
        return ''
    
    def repeat_title(self):
        if (not self.repeat) or (self.repeat == NONE):
            return _('Repeat')
        if (self.repeat_num == 1):
            if (self.repeat == WORKDAYS):
                return REPEAT[WEEKLY][1]
            return REPEAT[self.repeat][1]
        
        rn = ''
        if self.repeat:
            rn = REPEAT_NAME[self.repeat]
        return '{} {} {}'.format(_('Once every'), self.repeat_num, rn)
    
    def repeat_info(self):
        if (self.repeat == WEEKLY):
            if (self.repeat_days == 0):
                return formats.date_format(self.stop, 'l')
            if (self.repeat_days == 1+2+4+8+16):
                return str(_('Work days'))
            ret = ''
            monday = datetime(2020, 7, 6, 0, 0)
            for i in range(7):
                if (self.repeat_days & (1 << i)):
                    if (ret != ''):
                        ret += ', '
                    ret += formats.date_format(monday +timedelta(i), 'l')
            return ret
        return ''
    
    def next_remind_time(self):
        if ((not self.remind) and (not self.first_remind) and (not self.last_remind)) or (not self.stop):
            return None
        if self.first_remind:
            rmd = self.first_remind
        elif self.remind:
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

    def expen_amount(self, currency=None):
        amount = None
        if self.expen_price:
            amount = self.expen_price
            if self.expen_qty:
                amount = self.expen_price * self.expen_qty

        if amount and (currency == 'USD') and (self.price_unit != 'USD') and self.expen_rate_usd:
            amount = amount / self.expen_rate_usd

        return amount

    def expen_item_summary(self):
        res = []
        if self.expen_qty and self.expen_price and self.price_unit:
            value = self.expen_price * self.expen_qty
            res.append(currency_repr(value, self.price_unit))
        return res

    def correct_groups_qty(self, mode, group_id=None, role=None, todo_only=False):
        if (mode == GIQ_ADD_TASK) and Group.objects.filter(id=group_id).exists():
            group = Group.objects.filter(id=group_id).get()
            if (group.determinator == 'group') or (group.determinator == None):
                TaskGroup.objects.create(task=self, group=group, role=group.role)
                if not self.completed:
                    if group.act_items_qty == None:
                        group.act_items_qty = 0
                    group.act_items_qty += 1
                    group.save()
                    return True
        if (mode == GIQ_DEL_TASK) and role:
            tgs = TaskGroup.objects.filter(task=self.id, role=role)
            if (len(tgs) == 1):
                group = tgs[0].group
                if (not self.completed) and group and (group.act_items_qty != None) and (group.act_items_qty > 0):
                    group.act_items_qty -= 1
                    group.save()
                tgs[0].delete()
                return True
        if (mode == GIQ_CMP_TASK):
            for tg in TaskGroup.objects.filter(task_id=self.id):
                if tg.group and tg.group.act_items_qty != None:
                    if self.completed:
                        if not todo_only or (tg.group.role == ROLE_TODO):
                            tg.group.act_items_qty -= 1
                    else:
                        tg.group.act_items_qty += 1
                    tg.group.save()
        return False

    def delete_linked_items(self):
        for tg in TaskGroup.objects.filter(task=self.id):
            self.correct_groups_qty(GIQ_DEL_TASK, tg.group.role)
        Step.objects.filter(task=self.id).delete()
        Urls.objects.filter(task=self.id).delete()
        Hist.objects.filter(task=self.id).delete()

    def get_tuned_data(self):
        if (self.app_fuel != NUM_ROLE_PART):
            return None

        last_odo = None
        if Task.objects.filter(user=self.user.id, app_fuel__gt=0, task_1=self.task_1.id).exclude(car_odometr=None).exclude(car_odometr=0).exists():
            last_odo = Task.objects.filter(user=self.user.id, app_fuel__gt=0, task_1=self.task_1.id).exclude(car_odometr=None).exclude(car_odometr=0).order_by('-event')[0]
        if (not last_odo):
            return None

        # last_repl = None
        # if Task.objects.filter(user=self.user.id, app_fuel=NUM_ROLE_SERVICE, task_1=self.task_1.id, task_2=self.id).exists():
        #     last_repl = Task.objects.filter(user=self.user.id, app_fuel=NUM_ROLE_SERVICE, task_1=self.task_1.id, task_2=self.id).order_by('-event')[0]
        # if (not last_repl):
        #     return None

        # rest, tune_class = get_rest(self, last_odo, last_repl)
        # return [{'class': tune_class, 'info': rest}]
        return None

    def actualize_role_info(self, app, role, info=None):
        qnt = len(self.get_files_list(role))
        str_info = None
        if info:
            str_info = json.dumps(info)
        if qnt == 0 and info == None:
            TaskRoleInfo.objects.filter(task=self.id, app=app, role=role).delete()
        else:
            if not TaskRoleInfo.objects.filter(task=self.id, app=app, role=role).exists():
                TaskRoleInfo.objects.create(task=self, app=app, role=role, info=str_info, files_qnt=qnt)
            else:
                tri = TaskRoleInfo.objects.filter(task=self.id, app=app, role=role).get()
                tri.info = str_info
                tri.files_qnt = qnt
                tri.save()

    def get_group_name(self, role):
        if TaskGroup.objects.filter(task=self.id, role=role).exists():
            task_group = TaskGroup.objects.filter(task=self.id, role=role).get()
            return task_group.group.name
        return ''


GIQ_ADD_TASK = 1 # Task created
GIQ_DEL_TASK = 2 # Task deleted
GIQ_CMP_TASK = 3 # Task.completed changed

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
                        n = requests.get(self.href, headers=hearders, timeout=5)
                    except:
                        self.status = -2
                    if (self.status > 0):
                        self.status = 3
                        al = n.text
                        start = al.find('<title>')
                        stop = al.find('</title>')
                        if (start > 0) and (stop > start):
                            if ((stop - start) < 190):
                                self.title = al[start+7:stop]
                            else:
                                self.title = al[start+7:start+190] + '...'
                            self.title = ''.join(x if ord(x) < 65536 else '*' for x in self.title)
                            self.ststus = 4
            self.save()
        if (self.hostname and self.title):
            return self.hostname + ': ' + self.title
        if (self.hostname):
            return self.hostname
        if (self.title):
            return self.title
        return self.href

class TaskRoleInfo(models.Model):
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('task'))
    app = models.CharField(_('app name'), max_length=50, blank=False, default='todo', null=True)
    role = models.CharField(_('role name'), max_length=50, blank=False, default='todo', null=True)
    created = models.DateTimeField(_('creation time'), blank=True, default=datetime.now)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    info = models.CharField(_('role specific info'), max_length=1000, blank=True, default=None, null=True)
    files_qnt = models.IntegerField(_('number of attached files'), default=0, null=True)

    @classmethod
    def actualize(cls, user, item_id: int, role: str, info, attach_path: str):
        app = ROLE_APP[role]
        files_list = get_files_list_by_path_v2(user, role, item_id, attach_path)
        files_qty = len(files_list)
        if files_qty == 0 and info == None:
            TaskRoleInfo.objects.filter(task=item_id, app=app, role=role).delete()
        else:
            if not TaskRoleInfo.objects.filter(task=item_id, app=app, role=role).exists():
                item = Task.objects.filter(id=item_id).get()
                str_info = json.dumps(info)
                TaskRoleInfo.objects.create(task=item, app=app, role=role, info=str_info, files_qnt=files_qty)
            else:
                tri = TaskRoleInfo.objects.filter(task=item_id, app=app, role=role).get()
                tri.info = json.dumps(info)
                tri.files_qnt = files_qty
                tri.save()

def currency_item_repr(value, currency):
    if (round(value, 2) % 1):
        value = '{:,.2f} {}'.format(value, currency).replace(',', '`')
    else:
        value = '{:,.0f} {}'.format(value, currency).replace(',', '`')
    return value

def currency_repr(value, currency, color_class=''):
    if (round(value, 2) % 1):
        value = '{:,.2f} {}'.format(value, currency).replace(',', '`')
    else:
        value = '{:,.0f} {}'.format(value, currency).replace(',', '`')
    return {'value': value, 'color': color_class}


class Hist(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_('task'), related_name = 'task_hist')
    valid_until = models.DateTimeField(_('Valid until date'), blank=True, default=datetime.now)
    store_username = models.CharField(_('username'), max_length=150, blank=True, null=True)
    store_value = models.CharField(_('value'), max_length=128, null=True)
    store_params = models.IntegerField(_('generator parameters used'), null=True)
    info = models.TextField(_('Information'), blank=True, null=True)
    store_uuid = models.CharField(_('UUID'), max_length=100, blank=True, null=True)

# Browsing History
class VisitedHistory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'), related_name = 'visit_user')
    stamp = models.DateTimeField(_('visit time'), null=False)
    href = models.CharField(_('visited url'), max_length=200, blank=True)
    app = models.CharField(_('visited application'), max_length=200, blank=True)
    page = models.CharField(_('visited page'), max_length=200, blank=True)
    info = models.CharField(_('page info'), max_length=200, blank=True)
    icon = models.CharField(_('page icon'), max_length=30, blank=True, null=True)
    pinned = models.BooleanField(_('is pinned'), default=False, null=False)

    class Meta:
        verbose_name = _('visited page')
        verbose_name_plural = _('visited pages')

    def __str__(self):
        return self.app + ' - ' + self.page
    
    def title(self):
        title = None
        if not self.page and not self.info:
            title = ''
        if self.page and not self.info:
            title = self.page
        if not self.page and self.info:
            title = self.info
        if self.page and self.info:
            title = '{} [{}]'.format(self.page, self.info)
        if not title:
            return _(self.app).capitalize()
        else:
            return _(self.app).capitalize() + ' - ' + title
        
    def reverse_url(self):
        return self.href

class PassParams(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='store_user')
    length = models.IntegerField('Length', default = 20)
    uc = models.BooleanField('Upper case', default = True)
    lc = models.BooleanField('Lower case', default = True)
    dg = models.BooleanField('Digits', default = True)
    sp = models.BooleanField('Special symbols', default = True)
    br = models.BooleanField('Brackets', default = True)
    mi = models.BooleanField('Minus', default = True)
    ul = models.BooleanField('Underline', default = True)
    ac = models.BooleanField('Avoid confusion', default = True)
    un = models.CharField('Default username', max_length=160, blank=True, default='')

    @classmethod
    def get_new_value(cls, user):
        if (len(PassParams.objects.filter(user = user.id)) > 0):
            params = PassParams.objects.filter(user = user.id)[0]
        else:
            params = PassParams.objects.create(user = user)

        allowed_chars = ''
        
        if params.uc:
            allowed_chars = allowed_chars + 'ABCDEFGHJKLMNPQRSTUVWXYZ'
            if not params.ac:
                allowed_chars = allowed_chars + 'IO'
        
        if params.lc:
            allowed_chars = allowed_chars + 'abcdefghjkmnpqrstuvwxyz'
            if not params.ac:
                allowed_chars = allowed_chars + 'io'

        if params.dg:
            allowed_chars = allowed_chars + '23456789'
            if not params.ac:
                allowed_chars = allowed_chars + '10'

        if params.sp:
            allowed_chars = allowed_chars + '!@#$%^&*=+'

        if params.br:
            allowed_chars = allowed_chars + '()[]{}<>'
        
        if params.mi:
            allowed_chars = allowed_chars + '-'
        
        if params.ul:
            allowed_chars = allowed_chars + '_'

        if (allowed_chars == ''):
            allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*(-_=+)'

        ret_params = 0
        if params.uc:
            ret_params += 1
        if params.lc:
            ret_params += 2
        if params.dg:
            ret_params += 4
        if params.sp:
            ret_params += 8
        if params.br:
            ret_params += 16
        if params.mi:
            ret_params += 32
        if params.ul:
            ret_params += 64
        if params.ac:
            ret_params += 128

        ret_value = get_random_string(params.length, allowed_chars)
        return ret_params, params.un, ret_value

class TaskInfo(models.Model):
    """
    An Entity that can be a Task or something else
    """
    app = models.CharField('App', max_length=20, blank=True)
    num_role = models.IntegerField('Task Role id', null=True)
    role = models.CharField('Role', max_length=20, blank=True)
    icon = models.CharField('Icon', max_length=20, blank=True)
    subgroup_id = models.IntegerField('Subgroup id', null=True)
    subgroup_name = models.CharField('Name', max_length=200, blank=True)
    group_id = models.IntegerField('Group id', null=True)
    group_name = models.CharField('Group name', max_length=200, blank=True)
    related = models.CharField('List of related roles', max_length=1000, blank=True)
    custom_attr = models.CharField('Custom role attributes', max_length=500, blank=True)
    task_descr = models.CharField('Cutted to 85 symbols task info', max_length=85, blank=True)
    has_files = models.IntegerField('Has files', null=True)
    has_links = models.IntegerField('Has links', null=True)
    #------------ Task ------------
    id = models.IntegerField('Id', primary_key=True, null=False)
    user_id = models.IntegerField('User id', null=False)
    name = models.CharField('Name', max_length=200, blank=False)
    event = models.DateTimeField('Event date', blank=True, null=True)
    start = models.DateField('Start date', blank=True, null=True)
    stop = models.DateTimeField('Termin', blank=True, null=True)
    completed = models.BooleanField('Completed', default=False)
    completion = models.DateTimeField('Completion time', blank=True, null=True)
    in_my_day = models.BooleanField('In My day', default=False)
    important = models.BooleanField('Important', default=False)
    remind = models.DateTimeField('Remind', blank=True, null=True)
    repeat = models.IntegerField('Repeat', blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    categories = models.TextField('Categories', blank=True, null=True)
    info = models.TextField('Information', blank=True, null=True)
    app_fuel = models.IntegerField('Role in application Fueling', choices=FUEL_ROLE_CHOICE, default=NONE, null=True)
    created = models.DateTimeField('Creation time', default=datetime.now)
    active = models.BooleanField('Is active navigation item', null=True)
    task_1_id = models.IntegerField('task_1 id', null=True)
    sort = models.CharField('Sort code', max_length=50, blank=True)
    #------------- Store --------------
    store_username = models.CharField(_('username'), max_length=150, blank=True, null=True)
    store_value = models.CharField(_('value'), max_length=128, null=True)
    #------------- Apart --------------
    apart_has_el = models.BooleanField('Has electricity', null=True)
    apart_has_hw = models.BooleanField('Has hot water', null=True)
    apart_has_cw = models.BooleanField('Has cold water', null=True)
    apart_has_gas = models.BooleanField('Has gas', null=True)
    apart_has_ppo = models.BooleanField('Payments to the partnership of owners', null=True)
    apart_has_tv = models.BooleanField('Has Internet/TV', null=True)
    apart_has_phone = models.BooleanField('Has phone', null=True)
    apart_has_zkx = models.BooleanField('Has ZKX', null=True)


    class Meta:
        managed = False
        db_table = 'vw_tasks'

    def get_absolute_url(self):
        if not self.app:
            return '/'
        base_role = list(ROLES_IDS[self.app].values())[0]
        if (self.role == ROLE_BY_NUM[base_role]):
            self.role = None
        try:
            if self.role:
                url = reverse(self.app + ':' + self.role + '-item', args = [self.id])
            else:
                url = reverse(self.app + ':item', args = [self.id])
            return url
        except NoReverseMatch:
            return '/'

    def b_expired(self):
        if self.completed:
            return False
        if self.stop:
            return (self.stop < datetime.now()) and ((self.stop.date() != date.today()) or (self.stop.hour != 0) or (self.stop.minute != 0))
        return False

    def termin_date(self):
        if not self.stop:
            return _('Set due date')
        if self.b_expired():
            s = str(_('Expired')) + ', '
        else:
            s = str(_('Termin')) + ': '
        return s + str(nice_date(self.stop))

    def get_tuned_data(self):
        if (self.app_fuel != NUM_ROLE_PART):
            return None
        task = Task.objects.filter(id=self.id).get()
        return task.get_tuned_data()

    def get_roles(self):
        task = Task.objects.filter(id=self.id).get()
        return task.get_roles()

    def remind_active(self):
        return self.remind and (not self.completed) and (self.remind > datetime.now())

    def get_custom_attr(self):
        if self.custom_attr:
            return json.loads(self.custom_attr)

    def get_categories(self):
        if not self.categories:
            return None
        return [{
            'name': categ,
            'color': 'category-design-' + CATEGORY_DESIGN[reduce(lambda x, y: x + ord(y), categ, 0) % 6], } for categ in self.categories.split()]

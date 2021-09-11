import calendar
from urllib.parse import urlparse
import requests

from datetime import date, time, datetime, timedelta
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from rest_framework.reverse import reverse

from task.const import *
from task.categories import get_categories_list
from task.files import get_files_list
from rusel.utils import nice_date
#from todo.const import *

class Group(models.Model):
    """
    Task groups
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='task_group')
    role = models.CharField(_('role name'), max_length = 50, blank = False, default = 'todo', null = True)
    node = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name=_('node'), blank=True, null=True)
    name = models.CharField(_('group name'), max_length=200, blank=False)
    sort = models.CharField(_('sort code'), max_length=50, blank=True)
    created = models.DateTimeField(_('creation time'), blank=True, auto_now_add=True)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)

    class Meta:
        verbose_name=_('task group')
        verbose_name_plural = _('task groups')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return '.' * self.level() + self.name

    def qty(self):
        return len(TaskGroup.objects.filter(group=self.id))

    def s_id(self):
        return str(self.id)
    
    def get_shifted_name(self):
        return '.'*self.level()*2 + self.name
    
    def edit_url(self):
        return get_app_by_role(self.role) + ':group-detail'

    def level(self):
        ret = 0
        node = self.node
        while node:
            ret += 1
            node = node.node
        return ret

    def is_leaf(self):
        return not Group.objects.filter(node=self.id).exists()

    """
    @classmethod
    def scan_node(cls, tree, group_id):
        for x in cls.objects.filter(node=group_id).order_by('sort'):
            tree.append((x.id, '.' * x.level() * 2 + x.name))
            cls.scan_node(tree, x.id)
    
    @classmethod
    def get_tree(cls, user_id, app):
        tree = []
        tree.append((0, '-----------'))
        for x in cls.objects.filter(user=user_id, app=app, node=None).order_by('sort'):
            tree.append((x.id, x.name))
            cls.scan_node(tree, x.id)
        return tree
    """

class Task(models.Model):
    """
    An Entity that can be a Task or something else
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name = 'task_user')
    name = models.CharField(_('name'), max_length=200, blank=False)
    start = models.DateField(_('start date'), blank=True, null=True)
    stop = models.DateTimeField(_('termin'), blank=True, null=True)
    completed = models.BooleanField(_('completed'), default=False)
    completion = models.DateTimeField(_('completion time'), blank=True, null=True, default=None)
    in_my_day = models.BooleanField(_('in my day'), default=False)
    important = models.BooleanField(_('important'), default=False)
    remind = models.DateTimeField(_('remind'), blank=True, null=True)
    last_remind = models.DateTimeField(_('last remind'), blank=True, null=True)
    repeat = models.IntegerField(_('repeat'), blank=True, null=True, choices=REPEAT_SELECT, default=NONE)
    repeat_num = models.IntegerField(_('repeat num'), blank=True, default=1)
    repeat_days = models.IntegerField(_('repeat days'), blank=True, default=0)
    categories = models.TextField(_('categories'), blank=True, default="")
    info = models.TextField(_('information'), blank=True, default="")
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
    created = models.DateTimeField(_('creation time'), auto_now_add=True)
    last_mod = models.DateTimeField(_('last modification time'), blank=True, auto_now=True)
    groups = models.ManyToManyField(Group, through='TaskGroup')

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    def __str__(self):
        return self.name

    def get_item_app(self):
        if (self.app_task == NUM_ROLE_TODO):
            return 'todo'
        if (self.app_note == NUM_ROLE_NOTE):
            return 'note'
        return None

    def get_absolute_url(self):
        app = self.get_item_app()
        if not app:
            return '/'
        id = self.id
        url = reverse(app + ':item-detail', args = [id])
        return url
    
    def marked_item(self):
        return self.completed

    def toggle_completed(self):
        next = None
        if (not self.completed) and self.repeat:
            if not self.start:
                self.start = self.stop # For a repeating task, remember the deadline that is specified in the first iteration in order to use it to adjust the next steps
            next = self.next_iteration()
        self.completed = not self.completed
        if self.completed:
            if not self.stop:
                self.stop = date.today()
            self.completion = datetime.now()
        else:
            self.completion = None
        self.save()
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
            return (self.stop.date() < date.today())
        return False

    def termin_date(self):
        d = self.stop
        if not d:
            return _('set due date').capitalize()
        if self.b_expired():
            s = str(_('expired')).capitalize() + ', '
        else:
            s = str(_('termin')).capitalize() + ': '
        return s + str(nice_date(d.date()))
            
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
    
    def s_repeat(self):
        pass
    
    def repeat_s_days(self):
        pass
    
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
        delta = self.stop - rmd.date()
        next = self.next_iteration()
        if (not next):
            return None
        rd = next - delta
        return datetime(rd.year, rd.month, rd.day, rmd.hour, rmd.minute, rmd.second)

    def get_info(self):
        ret = []
        
        """
        if self.grp: # and (app_param.restriction != 'list'):
            ret.append({'text': self.grp.name})
        """

        if self.in_my_day: # and (app_param.restriction != 'myday'):
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'icon': 'myday', 'color': 'black', 'text': _('My day')})

        step_total = 0
        step_completed = 0
        for step in Step.objects.filter(task=self.id):
            step_total += 1
            if step.completed:
                step_completed += 1
        if (step_total > 0):
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': '{} {} {}'.format(step_completed, _('out of'), step_total)})

        d = self.stop
        if d:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            s = self.termin_date()
            repeat = 'repeat'
            if self.b_expired():
                if self.completed:
                    icon = 'termin'
                    color = ''
                else:
                    icon = 'termin-expired'
                    color = 'expired'
                    repeat = 'repeat-expired'
                ret.append({'icon': icon, 'color': color, 'text': s})
            elif (self.stop == date.today()):
                if self.completed:
                    icon = 'termin'
                    color = ''
                else:
                    icon = 'termin-actual'
                    color = 'actual'
                    repeat = 'repeat-actual'
                ret.append({'icon': icon, 'color': color, 'text': s})
            else:
                ret.append({'icon': 'termin', 'text': s})
    
            if (self.repeat != 0):
                ret.append({'icon': repeat})
    
        files = (len(get_files_list(self.user, 'todo', 'task', self.id)) > 0)
    
        if ((self.remind != None) and (self.remind >= datetime.now())) or self.info or files:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            if ((self.remind != None) and (self.remind >= datetime.now())):
                ret.append({'icon': 'remind'})
            if self.info:
                ret.append({'icon': 'notes'})
            if files:
                ret.append({'icon': 'attach'})
    
        if self.categories:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            categs = get_categories_list(self.categories)
            for categ in categs:
                ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
        if self.completed:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': '{}: {}'.format(_('completion').capitalize(), self.completion.strftime('%d.%m.%Y'))})

        return ret

    def s_in_my_day(self):
        if self.in_my_day:
            return _('Added in "My day"')
        else:
            return _('Add in "My day"')


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return date(year, month, day)
    


class Step(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'), related_name='task_step')
    task = models.ForeignKey(Task, on_delete = models.CASCADE, verbose_name = _('step task'))
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)
    name = models.CharField(_('step name'), max_length = 200, blank = False)
    sort = models.CharField(_('sort code'), max_length = 50, blank = True)
    completed = models.BooleanField(_('step is completed'), default = False)

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
    role = models.CharField(_('role name'), max_length = 50, blank = False, default = 'todo', null = True)
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)

class Urls(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=_('task'), related_name = 'task_urlsr')
    num = models.IntegerField(_('sort number'), default=0, null=True)
    href = models.URLField(_('URL'), max_length=2000, null=True, blank=True)
    status = models.IntegerField(_('status'), default=0, null=True)
    hostname = models.CharField(_('hostname'), max_length=200, blank=True, null=True)
    title = models.CharField(_('page title'), max_length=200, blank=True, null=True)
    created = models.DateTimeField(_('creation time'), blank = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True)

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

class BaseCustomTask(Task):

    @classmethod
    def from_Task(cls, a: Task, grp):
        custom_obj = cls()
        for key, value in a.__dict__.items():
            custom_obj.__dict__[key] = value
        custom_obj.__dict__['grp'] = grp
        return custom_obj



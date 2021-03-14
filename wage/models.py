from datetime import datetime, date
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

app_name = 'wage'


class Period(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    dBeg = models.DateField(_('month/year'), default = datetime.today)
    planDays  = models.IntegerField(_('plan, days'), blank = True)
    AvansDate = models.DateField(_('prepayment date'), blank = True, null = True)
    PaymentDate = models.DateField(_('payment date'), blank = True, null = True)
    AvansRate = models.DecimalField(_('prepayment rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    PaymentRate = models.DecimalField(_('payment rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    DebtInRate = models.DecimalField(_('incoming debt rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    Part2Date = models.DateField(_('second payment date'), blank = True, null = True)
    Part2Rate = models.DecimalField(_('second payment rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    active = models.BooleanField(_('current billing period'), default = False)

    class Meta:
        verbose_name = _('billing period')
        verbose_name_plural = _('billing periods')

    def __str__(self):
        return self.name()

    def name(self):
        return self.dBeg.strftime('%Y %b')

    def get_info(self):
        ret = []
        ret.append({ 'text': str(self.planDays) })
        if self.AvansDate:
            ret.append({ 'icon': 'separator', 'text': _('prepayment').capitalize() + ' ' + self.AvansDate.strftime('%d.%m.%Y') })
        if self.PaymentDate:
            ret.append({ 'icon': 'separator', 'text': _('payment').capitalize() + ' ' + self.PaymentDate.strftime('%d.%m.%Y') })
        if self.Part2Date:
            ret.append({ 'icon': 'separator', 'text': _('second payment').capitalize() + ' ' + self.Part2Date.strftime('%d.%m.%Y') })
        return ret

    def marked_item(self):
        return self.active

    def prev(self):
        y = self.dBeg.year
        m = self.dBeg.month
        if (m == 1):
            m = 12
            y -= 1
        else:
            m -= 1
        d = datetime(y, m, 1).date()
        if Period.objects.filter(user = self.user.id, dBeg = d).exists():
            return Period.objects.filter(user = self.user.id, dBeg = d).get()
        return None

def deactivate_all(user_id, period_id):
    for item in Period.objects.filter(user = user_id, active = True).exclude(id = period_id):
        item.active = False
        item.save()

def set_active(user_id, period_id):
    if Period.objects.filter(user = user_id, id = period_id).exists():
        item = Period.objects.filter(user = user_id, id = period_id).get()
        deactivate_all(user_id, item.id)
        item.active = True
        item.save()



class Depart(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name = models.CharField(_('name'), max_length = 1000)
    sort = models.CharField(_('sorting'), max_length = 100, blank = True)
    is_open = models.BooleanField(_('node is open'), default = False)
    active = models.BooleanField(_('current department'), default = False)

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return self.name

    def set_active(self):
        for item in Depart.objects.filter(user = self.user.id, active = True).exclude(id = self.id):
            item.active = False
            item.save()
        self.active = True
        self.save()
        
    def created(self):
        hist = DepHist.objects.filter(depart = self.id).order_by('dBeg')
        if (len(hist) > 0):
            return hist[0].dBeg
        return None

class DepHist(models.Model):
    dBeg = models.DateField(_('begin date'), default = datetime.today)
    depart = models.ForeignKey(Depart, on_delete = models.CASCADE, null = True, related_name = 'D', verbose_name = _('department'))
    node = models.ForeignKey(Depart, on_delete = models.CASCADE, blank = True, null = True, related_name = 'N', verbose_name = _('superior department'))

    class Meta:
        verbose_name = _('department history')
        verbose_name_plural = _('departments history')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.dBeg.strftime('%d.%m.%Y') + ' - ' + self.depart.name

    def name(self):
        if self.dBeg:
            return self.dBeg.strftime('%d.%m.%Y')
        else:
            return '__.__.____'

    def get_info(self):
        ret = []
        if self.node:
            ret.append({ 'text': self.node.name })
        return ret


class Post(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name = models.CharField(_('name'), max_length = 1000, blank = False)

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    fio = models.CharField(_('full name'), max_length = 100, blank = False)
    login = models.CharField(_('login'), max_length = 50, blank = True)
    sort = models.CharField(_('sorting'), max_length = 100, blank = True)
    email = models.CharField(_('email'), max_length = 100, blank = True)
    passw = models.CharField(_('password'), max_length = 50, blank = True)
    born = models.DateField(_('birthday'), blank = True, null = True)
    phone = models.CharField(_('phone'), max_length = 50, blank = True)
    addr = models.CharField(_('address'), max_length = 1000, blank = True)
    info = models.TextField(_('information'), blank = True, default = "")
    active = models.BooleanField(_('current employee'), default = False)

    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')

    def __str__(self):
        return self.fio

    def name(self):
        return self.fio

    def get_info(self):
        ret = []
        ret.append({'text': self.login })
        if self.born:
            ret.append({'icon': 'separator', 'text': self.born.strftime('%d.%m.%Y') })
        if self.email:
            ret.append({'icon': 'separator', 'text': self.email })
        if self.phone:
            ret.append({'icon': 'separator', 'text': self.phone })
        if self.addr:
            ret.append({'icon': 'separator', 'text': self.addr })
        if self.info:
            ret.append({'icon': 'separator' })
            ret.append({'icon': 'notes' })
        return ret

    def fired(self, on_date):
        if Appoint.objects.filter(employee = self.id, dBeg__lte = on_date).exists():
            appoint = Appoint.objects.filter(employee = self.id, dBeg__lte = on_date).order_by('-dBeg')[0]
            if Depart.objects.filter(user = self.user.id, name = 'Уволенные').exists():
                fire_dep = Depart.objects.filter(user = self.user.id, name = 'Уволенные').get()
                if (appoint.depart.id == fire_dep.id):
                    return True
            md = date.min
            return appoint.dEnd and (appoint.dEnd > md) and (appoint.dEnd < on_date)
        return True

    def set_active(self):
        for item in Employee.objects.filter(user = self.user.id, active = True).exclude(id = self.id):
            item.active = False
            item.save()
        self.active = True
        self.save()


class FioHist(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    dEnd = models.DateField(_('use before this date'), default = datetime.today)
    fio = models.CharField(_('surname'), max_length = 100, blank = False)
    info = models.TextField(_('information'), blank = True, default = "")

    class Meta:
        verbose_name = _('surname changes')
        verbose_name_plural = _('surnames changes')

    def __str__(self):
        return self.employee.fio + ': ' + self.fio + ' ' + gettext('before') + ' ' + self.dEnd.strftime('%d.%m.%Y')

    def name(self):
        return self.fio

    def get_info(self):
        ret = []
        ret.append({ 'text': str(self.dEnd.year) })
        if self.info:
            ret.append({ 'icon': 'separator' })
            ret.append({ 'icon': 'notes', 'text': self.info })
        return ret

class Child(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    born = models.DateField(_('birthday'), blank = True, null = True)
    sort = models.CharField(_('sorting').capitalize(), max_length = 100, blank = True)
    name = models.CharField(_('name'), max_length = 100, blank = False)
    info = models.TextField(_('information'), blank = True, default = "")

    class Meta:
        verbose_name = _('child')
        verbose_name_plural = _('children')

    def __str__(self):
        bd = ''
        if self.born:
            bd = ' ' + gettext('was born on') + ' ' + self.born.strftime('%d.%m.%Y')
        return self.employee.fio + ': ' + self.name + bd

    def get_info(self):
        ret = []
        if self.born:
            ret.append({ 'text': str(self.born.year) })
        if self.info:
            add_separator(ret)
            ret.append({ 'icon': 'notes', 'text': self.info })
        return ret


class Appoint(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    tabnum = models.CharField(_('personnel number'), max_length = 50, blank = True)
    dBeg = models.DateField(_('contract from'), blank = True, null = True)
    dEnd = models.DateField(_('contract until'), blank = True, null = True)
    salary = models.DecimalField(_('salary'), blank = False, default=0.0, max_digits = 15, decimal_places = 2)
    currency = models.CharField(_('currency'), max_length = 10, blank = True)
    depart = models.ForeignKey(Depart, on_delete = models.CASCADE, verbose_name = _('department'))
    post = models.ForeignKey(Post, on_delete = models.CASCADE, blank = True, null = True, verbose_name = _('post'))
    taxded = models.DecimalField(_('income tax relief'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    info = models.TextField(_('information'), blank = True, default = "")

    class Meta:
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')

    def name(self):
        s_post = ''
        if self.post:
            s_post = ' - ' + self.post.name
        s_dep = ''
        if self.depart:
            s_dep = ' ' + self.depart.name
        s_per = ''
        if self.dBeg:
            if self.dEnd:
                s_per = '{} - {}'.format(self.dBeg.strftime('%d.%m.%Y'), self.dEnd.strftime('%d.%m.%Y'))
            else:
                s_per = '{} {}'.format(_('from'), self.dBeg.strftime('%d.%m.%Y'))
        else:
            if self.dEnd:
                s_per = '{} {}'.format(_('until'), self.dEnd.strftime('%d.%m.%Y'))
        return  s_per + s_dep + s_post

    def __str__(self):
        return self.name()

    def get_info(self):
        ret = []
        ret.append({ 'text': str(self.salary) + ' ' + self.currency })
        if self.info:
            ret.append({ 'icon': 'separator' })
            ret.append({ 'icon': 'notes', 'text': self.info })
        return ret


class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    dBeg = models.DateField(_('from').capitalize(), blank = True, null = True)
    dEnd = models.DateField(_('until').capitalize(), blank = True, null = True)
    institution = models.CharField(_('university').capitalize(), max_length = 1000, blank = True)
    course = models.CharField(_('course').capitalize(), max_length = 1000, blank = True)
    specialty = models.CharField(_('specialty').capitalize(), max_length = 1000, blank = True)
    qualification = models.CharField(_('qualification').capitalize(), max_length = 1000, blank = True)
    document = models.CharField(_('document').capitalize(), max_length = 1000, blank = True)
    number = models.CharField(_('number').capitalize(), max_length = 100, blank = True)
    city = models.CharField(_('city').capitalize(), max_length = 100, blank = True)
    docdate = models.DateField(_('document date').capitalize(), blank = True, null = True)
    info = models.TextField(_('information').capitalize(), blank = True, default = "")

    class Meta:
        verbose_name = _('education').capitalize()
        verbose_name_plural = _('educations').capitalize()

    def s_beg(self):
        if (self.dBeg == None):
            return '__.__.____'
        else:
            return self.dBeg.strftime('%d.%m.%Y')

    def s_end(self):
        if (self.dEnd == None):
            return '__.__.____'
        else:
            return self.dEnd.strftime('%d.%m.%Y')

    def educ_year(self):
        if self.dEnd:
            return str(self.dEnd.year)
        if self.dBeg:
            return str(self.dBeg.year)
        return '????'

    def name(self):
        if self.institution:
            return self.educ_year() + ' - ' + self.institution
        if self.specialty:
            return self.educ_year() + ' - ' + self.specialty
        if self.qualification:
            return self.educ_year() + ' - ' + self.qualification
        return self.educ_year()

    def get_info(self):
        ret = []
        if self.dBeg:
            if self.dEnd:
                ret.append({ 'text': '{} {} {} {}'.format(_('from'), self.dBeg.strftime('%m.%Y'), _('until'), self.dEnd.strftime('%m.%Y')) })
            else:
                ret.append({ 'text': '{} {}'.format(_('from'), self.dBeg.strftime('%m.%Y')) })
        else:
            if self.dEnd:
                ret.append({ 'text': '{} {}'.format(_('in'), self.dEnd.strftime('%m.%Y')) })

        if self.course:
            add_separator(ret)
            ret.append({ 'text': self.course })

        if self.institution and self.specialty:
            add_separator(ret)
            ret.append({ 'text': self.specialty })

        if (self.institution or self.specialty) and self.qualification:
            add_separator(ret)
            ret.append({ 'text': self.qualification })

        if self.document or self.number:
            add_separator(ret)
            if self.document:
                doc = self.document
            else:
                doc = _('document')
            nm = ''
            if self.number:
                nm = '№{}'.format(self.number)
            dt = ''
            if self.docdate:
                dt = '{} {}'.format(_('from'), self.docdate.strftime('%d.%m.%Y'))
            ret.append({ 'text': '{} {} {}'.format(doc, nm, dt) })

        if self.info:
            add_separator(ret)
            ret.append({ 'icon': 'notes', 'text': self.info })
        return ret

    def __str__(self):
        return self.employee.fio + ': ' + self.s_beg() + ' - ' + self.s_end() + ' ' + self.institution + ' - ' + self.specialty

def add_separator(info):
    if info:
        info.append({ 'icon': 'separator' })

class EmplPer(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    period = models.ForeignKey(Period, on_delete = models.CASCADE, verbose_name = _('billing period'))
    factDays = models.DecimalField(_('fact, days'), blank = True, null = True, max_digits = 2, decimal_places = 0)
    debtIn = models.DecimalField(_('incoming debt, BYN'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    debtOut = models.DecimalField(_('outgoing debt, BYN'), blank = True, null = True, max_digits = 15, decimal_places = 2)
    salaryRate = models.DecimalField(_('salary rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    privilege = models.DecimalField(_('income tax relief'), blank = True, null = True, max_digits = 15, decimal_places = 2)

    class Meta:
        verbose_name = _('employee billing period')
        verbose_name_plural = _('employee billing periods')

    def __str__(self):
        return self.employee.fio + ': ' + str(self.period)
  
class PayTitle(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = _('user'))
    name = models.CharField(_('name'), max_length = 100, blank = False)

    class Meta:
        verbose_name = _('name of accrual or payment')
        verbose_name_plural = _('names of accruals and payments')

    def __str__(self):
        return self.name

class Payment(models.Model):
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE, verbose_name = _('employee'))
    period = models.ForeignKey(Period, on_delete = models.CASCADE, verbose_name = _('billing period'))
    direct = models.IntegerField(_('direction'), help_text = _('0 - accrual, 1 - payment'))
    payed = models.DateField(_('payed'), blank = True, null = True)
    sort = models.CharField(_('sorting'), max_length = 100, blank = True)
    title = models.ForeignKey(PayTitle, on_delete = models.CASCADE, verbose_name = _('name'), null = True)
    value = models.DecimalField(_('summa'), blank = False, default = 0.0, max_digits = 15, decimal_places = 2)
    currency = models.CharField(_('currency'), max_length = 10, blank = True)
    rate = models.DecimalField(_('rate'), blank = True, null = True, max_digits = 15, decimal_places = 4)
    info = models.TextField(_('information'), blank = True, default = "")

    class Meta:
        verbose_name = _('accrual or payment')
        verbose_name_plural = _('accruals and payments')

    def __str__(self):
        return self.employee.fio + ' ' + str(self.period) + ': ' + self.title.name + ' - ' + str(self.value) + ' ' + self.currency

    def name(self):
        if self.title:
            return self.title.name + ' - ' + str(self.value) + ' ' + self.currency
        else:
            return str(self.value) + ' ' + self.currency

    def get_info(self):
        ret = []
        if self.payed:
            ret.append({ 'text': self.payed.strftime('%d.%m.%Y') })

        if self.rate:
            add_separator(ret)
            ret.append({ 'text': self.rate })

        if self.info:
            add_separator(ret)
            ret.append({ 'icon': 'notes', 'text': self.info })
        return ret



from datetime import datetime, date
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import User


class Period(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    dBeg = models.DateField(_('begin'), default=timezone.now)
    planDays  = models.IntegerField(_('plan days'), blank=True)
    AvansDate = models.DateField(_('prepaid date'), blank=True, null=True)
    PaymentDate = models.DateField(_('pay date'), blank=True, null=True)
    AvansRate = models.DecimalField(_('prepaid rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    PaymentRate = models.DecimalField(_('pay rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    DebtInRate = models.DecimalField(_('credit rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    Part2Date = models.DateField(_('second pay date'), blank=True, null=True)
    Part2Rate = models.DecimalField(_('second pay rate'), blank=True, null=True, max_digits=15, decimal_places=4)

    class Meta:
        verbose_name = _('billing period')
        verbose_name_plural = _('billing periods')

    def __str__(self):
        return self.dBeg.strftime('%Y %b')


class Depart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=1000)
    sort = models.CharField(_('sort number'), max_length=100, blank=True)
    is_open = models.BooleanField(_('tree node is open'), default = False)

    class Meta:
        verbose_name = _('department')
        verbose_name_plural = _('departments')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.name

    def get_absolute_url(self):
        return reverse('wage:index')
        #return reverse('wage:depart', kwargs={'pk': self.pk})

class DepHist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    dBeg = models.DateField(_('begin'), default=timezone.now)
    dEnd = models.DateField(_('end'), blank=True, null=True)
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE, null=True, related_name='D', verbose_name=_('depart'))
    node = models.ForeignKey(Depart, on_delete=models.CASCADE, blank=True, null=True, related_name='N', verbose_name=_('node'))
    sort = models.CharField(_('sort number'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('department changes')
        verbose_name_plural = _('department changes ')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.dBeg.strftime('%d.%m.%Y') + ' - ' + self.depart.name


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=1000, blank=False)

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.name


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    fio = models.CharField(_('surname n.p.'), max_length=100, blank=False)
    login = models.CharField(_('login'), max_length=50, blank=True)
    sort = models.CharField(_('sort number'), max_length=100, blank=True)
    email = models.CharField(_('email'), max_length=100, blank=True)
    passw = models.CharField(_('password'), max_length=50, blank=True)
    born = models.DateField(_('birthday'), blank=True, null=True)
    phone = models.CharField(_('phone'), max_length=50, blank=True)
    addr = models.CharField(_('address'), max_length=1000, blank=True)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employees')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.fio

    def get_absolute_url(self):
        return reverse('wage:index')


class FioHist(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    dEnd = models.DateField(_('end'), default=timezone.now)
    fio = models.CharField(_('surname'), max_length=100, blank=False)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('surname changes')
        verbose_name_plural = _('surname changes ')

    def __str__(self):
        return self.employee.fio + ': ' + self.fio + ' ' + gettext('before') + ' ' + self.dEnd.strftime('%d.%m.%Y')

class Child(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    born = models.DateField(_('birthday'), blank=True, null=True)
    sort = models.CharField(_('sort number'), max_length=100, blank=True)
    name = models.CharField(_("child's name"), max_length=100, blank=False)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('child')
        verbose_name_plural = _('children')

    def __str__(self):
        return self.employee.fio + ': ' + self.name + ' ' + gettext('was born on') + ' ' + self.born.strftime('%d.%m.%Y')


class Appoint(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    tabnum = models.CharField(_('personnel number'), max_length=50, blank=True)
    dBeg = models.DateField(_('begin'), blank=True, null=True)
    dEnd = models.DateField(_('end'), blank=True, null=True)
    salary = models.DecimalField(_('salary'), blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=10, blank=True)
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE, verbose_name=_('department'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('post'))
    taxded = models.DecimalField(_('exemption'), blank=True, null=True, max_digits=15, decimal_places=2)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')

    def __str__(self):
        if (self.post == None):
            s_post = ''
        else:
            s_post = ' - ' + self.post.name
        return self.employee.fio + ': ' + self.dBeg.strftime('%d.%m.%Y') + ' ' + self.depart.name + s_post


class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    dBeg = models.DateField(_('begin'), blank=True, null=True)
    dEnd = models.DateField(_('end'), blank=True, null=True)
    institution = models.CharField(_('university'), max_length=1000, blank=True)
    course = models.CharField(_('training course'), max_length=1000, blank=True)
    specialty = models.CharField(_('specialty'), max_length=1000, blank=True)
    qualification = models.CharField(_('qualification'), max_length=1000, blank=True)
    document = models.CharField(_('document'), max_length=1000, blank=True)
    number = models.CharField(_('number'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    docdate = models.DateField(_('date'), blank=True, null=True)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('education')
        verbose_name_plural = _('educations')

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

    def __str__(self):
        return self.employee.fio + ': ' + self.s_beg() + ' - ' + self.s_end() + ' ' + self.institution + ' - ' + self.specialty

class EmplPer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name=_('period'))
    factDays = models.DecimalField(_('fact days'), blank=True, null=True, max_digits=2, decimal_places=0)
    debtIn = models.DecimalField(_('incoming balance'), blank=True, null=True, max_digits=15, decimal_places=2)
    debtOut = models.DecimalField(_('outgoing balance'), blank=True, null=True, max_digits=15, decimal_places=2)
    salaryRate = models.DecimalField(_('pay rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    privilege = models.DecimalField(_('exemption'), blank=True, null=True, max_digits=15, decimal_places=2)
    prevOut = models.DecimalField(_('incoming balance for check'), blank=True, null=True, max_digits=15, decimal_places=2)
    dBeg = models.DateField(_('begin'), blank=True, null=True)

    class Meta:
        verbose_name = _('employee period')
        verbose_name_plural = _('employee periods')

    def __str__(self):
        return self.employee.fio + ': ' + str(self.period)
  
class PayTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=100, blank=False)

    class Meta:
        verbose_name = _('payment title')
        verbose_name_plural = _('payment titles')

    def __str__(self):
        return '[' + self.user.username + '] ' + self.name

class Payment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name=_('period'))
    direct = models.IntegerField(_('direct'), help_text = _('0 - accrual, 1 - payment'))
    payed = models.DateField(_('date'), blank=True, null=True)
    sort = models.CharField(_('sort number'), max_length=100, blank=True)
    title = models.ForeignKey(PayTitle, on_delete=models.CASCADE, verbose_name=_('name'))
    value = models.DecimalField(_('summa'), blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=10, blank=True)
    rate = models.DecimalField(_('rate'), blank=True, null=True, max_digits=15, decimal_places=4)
    info = models.CharField(_('information'), max_length=1000, blank=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return self.employee.fio + ' ' + str(self.period) + ': ' + self.title.name + ' - ' + str(self.value) + ' ' + self.currency


class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name=_('period'), blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name=_('employee'), blank=True, null=True)

    class Meta:
        verbose_name = _('user parameters')
        verbose_name_plural = _('users parameters')

    def __str__(self):
        return '[' + self.user.username + '] ' + str(self.period) + ' - ' + self.employee.fio

    def d_scan(self):
        return datetime.now().date()
        """
        if (self.period == None):
            return datetime.now().date()
        else:
            return self.period.dBeg
        """


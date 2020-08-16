from datetime import datetime, date
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext


class Period(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    dBeg = models.DateField('Месяц/год', default=datetime.today)
    planDays  = models.IntegerField('План, дней', blank=True)
    AvansDate = models.DateField('Дата аванса', blank=True, null=True)
    PaymentDate = models.DateField('Дата выплаты', blank=True, null=True)
    AvansRate = models.DecimalField('Курс аванса', blank=True, null=True, max_digits=15, decimal_places=4)
    PaymentRate = models.DecimalField('Курс выплаты', blank=True, null=True, max_digits=15, decimal_places=4)
    DebtInRate = models.DecimalField('Курс входящего остатка', blank=True, null=True, max_digits=15, decimal_places=4)
    Part2Date = models.DateField('Дата выплаты второй части', blank=True, null=True)
    Part2Rate = models.DecimalField('Курс выплаты второй части', blank=True, null=True, max_digits=15, decimal_places=4)
    active = models.BooleanField('Текущий расчетный период', default = False)

    class Meta:
        verbose_name = 'Расчетный период'
        verbose_name_plural = 'Расчетные периоды'

    def __str__(self):
        return self.dBeg.strftime('%Y %b')

    def s_active(self):
        if self.active:
            return '*'
        else:
            return ''


class Depart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField('Наименование', max_length=1000)
    sort = models.CharField('Сортировка', max_length=100, blank=True)
    is_open = models.BooleanField('Узел иерархии раскрыт', default = False)

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wage:index')

class DepHist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь') # deprecated
    dBeg = models.DateField('Дата начала', default=datetime.today)
    dEnd = models.DateField('Дата окончания', blank=True, null=True) # deprecated
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE, null=True, related_name='D', verbose_name='Отдел')
    node = models.ForeignKey(Depart, on_delete=models.CASCADE, blank=True, null=True, related_name='N', verbose_name='Вышестоящий отдел')
    sort = models.CharField('Сортировка', max_length=100, blank=True) # deprecated

    class Meta:
        verbose_name = 'Изменение отдела'
        verbose_name_plural = 'Изменения отделов'

    def __str__(self):
        return '[' + self.user.username + '] ' + self.dBeg.strftime('%d.%m.%Y') + ' - ' + self.depart.name


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField('Наименование', max_length=1000, blank=False)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    fio = models.CharField('ФИО', max_length=100, blank=False)
    login = models.CharField('Логин', max_length=50, blank=True)
    sort = models.CharField('Сортировка', max_length=100, blank=True)
    email = models.CharField('Адрес электронной почты', max_length=100, blank=True)
    passw = models.CharField('Пароль', max_length=50, blank=True)
    born = models.DateField('День рождения', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    addr = models.CharField('Адрес жительства', max_length=1000, blank=True)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.fio

    def get_absolute_url(self):
        return reverse('wage:index')


class FioHist(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    dEnd = models.DateField('Использовалась до', default=datetime.today)
    fio = models.CharField('Фамилия', max_length=100, blank=False)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Изменение фамилии'
        verbose_name_plural = 'Изменения фамилий'

    def __str__(self):
        return self.employee.fio + ': ' + self.fio + ' ' + gettext('before') + ' ' + self.dEnd.strftime('%d.%m.%Y')

class Child(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    born = models.DateField('День рождения', blank=True, null=True)
    sort = models.CharField('Сормировка', max_length=100, blank=True)
    name = models.CharField('Имя', max_length=100, blank=False)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Ребёнок'
        verbose_name_plural = 'Дети'

    def __str__(self):
        return self.employee.fio + ': ' + self.name + ' ' + gettext('was born on') + ' ' + self.born.strftime('%d.%m.%Y')


class Appoint(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    tabnum = models.CharField('Табельный номер', max_length=50, blank=True)
    dBeg = models.DateField('Назначение с', blank=True, null=True)
    dEnd = models.DateField('Контракт до', blank=True, null=True)
    salary = models.DecimalField('Оклад', blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField('Валюта', max_length=10, blank=True)
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE, verbose_name='Отдел')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Должность')
    taxded = models.DecimalField('Льгота по ПН', blank=True, null=True, max_digits=15, decimal_places=2)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'

    def __str__(self):
        if (self.post == None):
            s_post = ''
        else:
            s_post = ' - ' + self.post.name
        return self.employee.fio + ': ' + self.dBeg.strftime('%d.%m.%Y') + ' ' + self.depart.name + s_post


class Education(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    dBeg = models.DateField('Начало', blank=True, null=True)
    dEnd = models.DateField('Окончание', blank=True, null=True)
    institution = models.CharField('ВУЗ', max_length=1000, blank=True)
    course = models.CharField('Учебный курс', max_length=1000, blank=True)
    specialty = models.CharField('Специальность', max_length=1000, blank=True)
    qualification = models.CharField('Квалификация', max_length=1000, blank=True)
    document = models.CharField('Документ', max_length=1000, blank=True)
    number = models.CharField('Номер', max_length=100, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    docdate = models.DateField('Дата документа', blank=True, null=True)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образования'

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
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Расчетный период')
    factDays = models.DecimalField('Факт, дней', blank=True, null=True, max_digits=2, decimal_places=0)
    debtIn = models.DecimalField('Входящий остаток, BYN', blank=True, null=True, max_digits=15, decimal_places=2)
    debtOut = models.DecimalField('Исходящий остаток, BYN', blank=True, null=True, max_digits=15, decimal_places=2)
    salaryRate = models.DecimalField('Курс оклада', blank=True, null=True, max_digits=15, decimal_places=4)
    privilege = models.DecimalField('Льгота по ПН', blank=True, null=True, max_digits=15, decimal_places=2)
    prevOut = models.DecimalField('Входящий остаток для сверки', blank=True, null=True, max_digits=15, decimal_places=2)
    dBeg = models.DateField('Дата начала', blank=True, null=True)

    class Meta:
        verbose_name = 'Расчетный период сотрудника'
        verbose_name_plural = 'Расчетные периоды сотрудников'

    def __str__(self):
        return self.employee.fio + ': ' + str(self.period)
  
class PayTitle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField('Наименование', max_length=100, blank=False)

    class Meta:
        verbose_name = 'Наименование начисления или выплаты'
        verbose_name_plural = 'Наименования начислений и выплат'

    def __str__(self):
        return self.name

class Payment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Расчетный период')
    direct = models.IntegerField('Направление', help_text = '0 - начисление, 1 - выплата')
    payed = models.DateField('Дата', blank=True, null=True)
    sort = models.CharField('Сортировка', max_length=100, blank=True)
    title = models.ForeignKey(PayTitle, on_delete=models.CASCADE, verbose_name='Наименование')
    value = models.DecimalField('Сумма', blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField('Валюта', max_length=10, blank=True)
    rate = models.DecimalField('Курс', blank=True, null=True, max_digits=15, decimal_places=4)
    info = models.CharField('Дополнительная информация', max_length=1000, blank=True)

    class Meta:
        verbose_name = 'Вид начисления или выплаты'
        verbose_name_plural = 'Виды начислений и выплат'

    def __str__(self):
        return self.employee.fio + ' ' + str(self.period) + ': ' + self.title.name + ' - ' + str(self.value) + ' ' + self.currency


class Params(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    # deprecated
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name='Расчетный период', blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник', blank=True, null=True)

    class Meta:
        verbose_name = 'Параметры пользователя'
        verbose_name_plural = 'Параметры пользователей'

    def __str__(self):
        if (not self.user):
            return 'user == None'

        if (not self.period):
            return '[' + self.user.username + '], period == None '
        
        if (not self.employee):
            return '[' + self.user.username + '] ' + str(self.period) + ' - employee == None'

        return '[' + self.user.username + '] ' + str(self.period) + ' - ' + self.employee.fio

    def d_scan(self):
        if (self.period == None):
            return datetime.now().date()
        else:
            return self.period.dBeg


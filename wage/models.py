from django.db import models
from django.utils import timezone
from datetime import date


class Period(models.Model):
    dBeg = models.DateField('Дата начала', default=timezone.now)
    #dEnd = models.DateField('Дата окончания', blank=True, null=True)
    planDays  = models.IntegerField('План, дней', blank=True)
    AvansDate = models.DateField('Дата аванса', blank=True, null=True)
    PaymentDate = models.DateField('Дата выплаты ЗП', blank=True, null=True)
    AvansRate = models.DecimalField('Курс аванса', blank=True, null=True, max_digits=15, decimal_places=4)
    PaymentRate = models.DecimalField('Курс ЗП', blank=True, null=True, max_digits=15, decimal_places=4)
    DebtInRate = models.DecimalField('Курс зачета с прошлого месяца', blank=True, null=True, max_digits=15, decimal_places=4)
    Part2Date = models.DateField('Дата выплаты 2 части', blank=True, null=True)
    Part2Rate = models.DecimalField('Курс 2 части', blank=True, null=True, max_digits=15, decimal_places=4)
    def __str__(self):
        return self.dBeg.month.__str__() + '.' + self.dBeg.year.__str__()


class Depart(models.Model):
    name = models.CharField('Наименование', max_length=1000)
    sort = models.CharField('Номер п/п', max_length=100, blank=True)
    def __str__(self):
        return self.name


class DepHist(models.Model):
    dBeg = models.DateField('Дата начала', default=timezone.now)
    dEnd = models.DateField('Дата окончания', blank=True, null=True)
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE, null=True, related_name='D',)
    node = models.ForeignKey(Depart, on_delete=models.CASCADE, blank=True, null=True, related_name='N',)
    sort = models.CharField('Номер п/п', max_length=100, blank=True)
    def __str__(self):
        return self.dBeg.__str__() + ' - ' + self.depart.__str__()


class Post(models.Model):
    name = models.CharField('Наименование', max_length=1000, blank=False)
    def __str__(self):
        return self.name


class Person(models.Model):
    fio = models.CharField('ФИО', max_length=100, blank=False)
    login = models.CharField('Логин', max_length=50, blank=True)
    sort = models.CharField('Номер п/п', max_length=100, blank=True)
    email = models.CharField('Электропочта', max_length=100, blank=True)
    passw = models.CharField('Пароль', max_length=50, blank=True)
    born = models.DateField('Дата рождения', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    addr = models.CharField('Адрес', max_length=1000, blank=True)
    info = models.CharField('Доп. информация', max_length=1000, blank=True)
    #dEmpl = models.DateField('Дата трудоустройства', blank=True, null=True)
    def __str__(self):
        return self.fio


class FioHist(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    dEnd = models.DateField('Дата окончания', default=timezone.now)
    fio = models.CharField('ФИО', max_length=100, blank=False)
    info = models.CharField('Доп. информация', max_length=1000, blank=True)
    def __str__(self):
        return self.dEnd.__str__() + ' - ' + self.fio
  

class Child(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    born = models.DateField('Дата рождения', blank=True, null=True)
    sort = models.CharField('Номер п/п', max_length=100, blank=True)
    name = models.CharField('Имя', max_length=100, blank=False)
    info = models.CharField('Доп. информация', max_length=1000, blank=True)
    def __str__(self):
        return self.name + ' ' + self.person.__str__()


class Appoint(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    tabnum = models.CharField('Табельный номер', max_length=50, blank=True)
    dBeg = models.DateField('Дата начала', blank=True, null=True)
    dEnd = models.DateField('Дата окончания', blank=True, null=True)
    salary = models.DecimalField('Оклад', blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField('Валюта', max_length=10, blank=True)
    depart = models.ForeignKey(Depart, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    taxded = models.DecimalField('Льгота по ПН', blank=True, null=True, max_digits=15, decimal_places=2)
    info = models.CharField('Доп. информация', max_length=1000, blank=True)
    def __str__(self):
        return self.person.__str__() + ' ' + self.dBeg.__str__() + ' ' + self.depart.__str__() + ' ' + self.post.__str__()


class Education(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    dBeg = models.DateField('Дата начала', blank=True, null=True)
    dEnd = models.DateField('Дата окончания', blank=True, null=True)
    institution = models.CharField('ВУЗ', max_length=1000, blank=True)
    course = models.CharField('Учебный курс', max_length=1000, blank=True)
    specialty = models.CharField('Специальность', max_length=1000, blank=True)
    qualification = models.CharField('Квалификация', max_length=1000, blank=True)
    document = models.CharField('Документ', max_length=1000, blank=True)
    number = models.CharField('Номер', max_length=100, blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    docdate = models.DateField('Дата документа', blank=True, null=True)
    info = models.CharField('Доп. информация', max_length=1000, blank=True)
    def __str__(self):
        return self.person.__str__() + ' - ' + self.dBeg.__str__() + ' - ' + self.dEnd.__str__() + ' - ' + self.institution

class PersPer(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    factDays = models.DecimalField('Фактически, дней', blank=True, null=True, max_digits=2, decimal_places=0)
    debtIn = models.DecimalField('Входящий остаток', blank=True, null=True, max_digits=15, decimal_places=2)
    debtOut = models.DecimalField('Исходящий остаток', blank=True, null=True, max_digits=15, decimal_places=2)
    salaryRate = models.DecimalField('Курс оклада', blank=True, null=True, max_digits=15, decimal_places=4)
    privilege = models.DecimalField('Льгота по ПН', blank=True, null=True, max_digits=15, decimal_places=2)
    prevOut = models.DecimalField('Вх. остаток - контроль с распечаткой', blank=True, null=True, max_digits=15, decimal_places=2)
    dBeg = models.DateField('Дата начала периода', blank=True, null=True)
    def __str__(self):
        return self.person.__str__() + ' - ' + self.period.__str__()
  
class PayTitle(models.Model):
    name = models.CharField('Наименования начислений и выплат', max_length=100, blank=False)
    def __str__(self):
        return self.name

class Payment(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    payed = models.DateField('Дата начисления или выплаты', blank=True, null=True)
    sort = models.CharField('Номер п/п', max_length=100, blank=True)
    title = models.ForeignKey(PayTitle, on_delete=models.CASCADE)
    value = models.DecimalField('Сумма', blank=False, default=0.0, max_digits=15, decimal_places=2)
    currency = models.CharField('Валюта', max_length=10, blank=True)
    rate = models.DecimalField('Курс', blank=True, null=True, max_digits=15, decimal_places=4)
    info = models.CharField('Комментарий', max_length=1000, blank=True)
    def __str__(self):
        return self.person.__str__() + ' - ' + self.period.__str__() + ' - ' + self.title.__str__() + ' - ' + self.value.__str__() + ' ' + self.currency.__str__()


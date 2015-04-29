# coding=UTF-8
from django.contrib.auth.models import User
from django.db import models
from datetime import date



class TGroup(models.Model):
  user     = models.ForeignKey(User)
  name     = models.CharField(u'Наименование', max_length = 200, blank = False)
  comment  = models.CharField(u'Описание', max_length = 2000, blank = True)
  active   = models.IntegerField(u'Активна', default = 0)
  sort     = models.IntegerField(u'Сортировка', default = 0)
  def __str__(self):
    return '[' + str(self.user) + '] ' + self.name + ' / ' + str(self.active) + ' / ' + self.comment


class Task(models.Model):
  user     = models.ForeignKey(User)
  grp      = models.ForeignKey(TGroup, blank = True, null = True)
  name     = models.CharField(u'Наименование', max_length = 200, blank = False)
  comment  = models.CharField(u'Описание', max_length = 2000, blank = True)
  pub_date = models.DateTimeField(u'Дата создания', default = date.today())
  due_date = models.DateTimeField(u'Время исполнения', blank = True, null = True, default = date.today())
  active   = models.IntegerField(u'Активна', default = 1)
  attrib   = models.IntegerField(u'Атрибуты задачи', default = 0, blank = True)
  def __str__(self):
    return '[' + str(self.user) + '] ' + self.name + ' / ' + str(self.pub_date) + ' / ' + str(self.due_date) + ' / ' + \
            str(self.active) + ' / ' + str(self.attrib) + ' / ' + self.comment
  def s_due(self):
    if (self.due_date == None):
      return '---'
    d = str(self.due_date.day)
    m = str(self.due_date.month)
    y = str(self.due_date.year)
    if (len(d) < 2):
      d = '0' + d
    if (len(m) < 2):
      m = '0' + m
    return d + '.' + m + '.' + y



def task_summary(_user):
  tasks = Task.objects.filter(user = _user)
  return u'Всего задач: <span style="color:yellow">' + str(len(tasks)) + u'</span>'


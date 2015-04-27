# coding=UTF-8
from django.contrib.auth.models import User
from django.db import models


class PirTable(models.Model):
  #user   = models.ForeignKey(User)
  name   = models.CharField(u'Таблица', max_length=200, blank=False)
  def __str__(self):
    return unicode(self.name)


class PirData(models.Model):
  table = models.ForeignKey(PirTable)
  rec   = models.CharField(u'Запись таблицы', max_length=1000, blank=False)
  def __str__(self):
    return unicode(self.table.name) + u' / ' + unicode(self.rec)

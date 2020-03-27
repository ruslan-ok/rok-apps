from django.contrib.auth.models import User
from django.db import models


class PirTable(models.Model):
  name   = models.CharField('Таблица', max_length = 200, blank = False)
  def __str__(self):
    return self.name


class PirPart(models.Model):
  table = models.ForeignKey(PirTable, on_delete=models.CASCADE)
  name  = models.CharField('Блок данных', max_length = 200, blank = False)
  def __str__(self):
    return self.table.name + ' / ' + str(self.rec)


class PirData(models.Model):
  table = models.ForeignKey(PirTable, on_delete=models.CASCADE)
  part = models.ForeignKey(PirPart, on_delete=models.CASCADE, default = 1)
  rec  = models.CharField('Запись таблицы', max_length = 1000, blank = False)
  def __str__(self):
    return self.part.table.name + ' / ' + self.part.name + ' / ' + self.rec

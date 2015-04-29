# coding=UTF-8
from django.contrib.auth.models import User
from django.db import models


class Apps(models.Model):
  user    = models.ForeignKey(User)
  name    = models.CharField(max_length=20, blank=False)
  page    = models.CharField(max_length=20, blank=False)
  title   = models.CharField(max_length=200, blank=True)
  summary = models.CharField(max_length=200, blank=True)
  def __str__(self):
    return self.name.encode('utf-8')


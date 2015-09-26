# coding=UTF-8
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django import forms
from datetime import date, datetime
import datetime

from task.models import TaskView

class TestForm(forms.Form):
    name = forms.CharField(label = 'Задача')

def do_test(request):
  form = TestForm()
  views = TaskView.objects.filter(user = request.user.id)
  return render(request, 'task/test.html', {'form': form, 'views': views, 'cur_view': views[0].name })

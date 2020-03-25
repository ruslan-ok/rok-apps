from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def rok_render(request, template, title): 
    current_site = get_current_site(request)
    context = {
       'user_info': request.user,
       'title': title,
       'site_header': current_site.name,
        }
    return render(request, template, context)

def index(request):
    if request.user.is_authenticated:
        title = _('Applications')
    else:
        title = get_current_site(request)
    return rok_render(request, 'index.html', title)

@login_required(login_url='account:login')
def news(request):
    return rok_render(request, 'news.html', _('News'))

@login_required(login_url='account:login')
def todo(request):
    return rok_render(request, 'todo.html', _('Tasks'))

@login_required(login_url='account:login')
def feedback(request):
    return rok_render(request, 'feedback.html', _('Feedback'))

@login_required(login_url='account:login')
def sample(request):
    return rok_render(request, 'sample.html', _('Sample'))

@login_required(login_url='account:login')
def fuel(request):
    return rok_render(request, 'sample.html', _('Fuel'))

@login_required(login_url='account:login')
def trip(request):
    return rok_render(request, 'sample.html', _('Trip'))

@login_required(login_url='account:login')
def apart(request):
    return render(request, 'sample.html')
    return rok_render(request, 'sample.html', _('Apartment'))

@login_required(login_url='account:login')
def proj(request):
    return rok_render(request, 'sample.html', _('Projects'))

@login_required(login_url='account:login')
def task(request):
    return rok_render(request, 'sample.html', _('Task'))

@login_required(login_url='account:login')
def wage(request):
    return rok_render(request, 'sample.html', _('Wage'))

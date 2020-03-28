from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def rok_render(request, template, title): 
    current_site = get_current_site(request)
    context = {
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
@permission_required('account.view_userext')
def news(request):
    return rok_render(request, 'news.html', _('News'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def todo(request):
    return rok_render(request, 'todo.html', _('Tasks'))

def feedback(request):
    return rok_render(request, 'feedback.html', _('Feedback'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def sample(request):
    return rok_render(request, 'sample.html', _('Sample'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def fuel(request):
    return rok_render(request, 'sample.html', _('Fuel'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def trip(request):
    return rok_render(request, 'sample.html', _('Trip'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def apart(request):
    return render(request, 'sample.html')
    return rok_render(request, 'sample.html', _('Apartment'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def proj(request):
    return rok_render(request, 'sample.html', _('Projects'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def task(request):
    return rok_render(request, 'sample.html', _('Task'))

@login_required(login_url='account:login')
@permission_required('account.view_userext')
def wage(request):
    return rok_render(request, 'sample.html', _('Wage'))

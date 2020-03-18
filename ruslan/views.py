# coding=UTF-8
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url, urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.utils.six.moves.urllib.parse import urlparse, urlunparse
from django.shortcuts import resolve_url, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

#from django.contrib.auth import authenticate, login

# Avoid shadowing the login() and logout() views below.
from django.contrib.auth import (REDIRECT_FIELD_NAME, login as auth_login,
    logout as auth_logout, get_user_model, update_session_auth_hash)

# Avoid shadowing the login() and logout() views below.
#from django.contrib.auth import (
#    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
#    logout as auth_logout, update_session_auth_hash,
#)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render_to_response
from trip.models  import trip_summary
from fuel.v_fuel  import fuel_summary
from apart.models import apart_summary
from proj.models  import proj_summary
from task.models  import task_summary


from apps.models import Apps

@csrf_protect
@login_required
def index(request):
    apps = Apps.objects.filter(user = request.user.id)
    if (len(apps) > 0):
        Apps.objects.all().delete()
    Apps(user = request.user, name = 'Проезд',   page='/trip',   title = '', summary = trip_summary(request.user.id)).save()
    Apps(user = request.user, name = 'Заправка', page='/fuel',   title = '', summary = fuel_summary(request.user.id)).save()
    Apps(user = request.user, name = 'Квартира', page='/apart',  title = '', summary = apart_summary(request.user.id)).save()
    Apps(user = request.user, name = 'Проекты',  page='/proj',   title = '', summary = proj_summary(request.user.id)).save()
    Apps(user = request.user, name = 'Задачи',   page='/task',   title = '', summary = task_summary(request.user.id)).save()
    apps = Apps.objects.all().filter(user = request.user.id)
    return render_to_response('index.html', {'page_title':'Приложения', 'apps':apps, 'user':request.user}, RequestContext(request))


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
        #else:
        #    return redirect('/not_valid/')
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)



def logout_vew(request):
    logout(request)
    return redirect('/login/')

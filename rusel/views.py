from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context, save_folder_id
from trip.models import trip_summary

#----------------------------------
# Index
#----------------------------------
def index(request):
    if request.user.is_authenticated:
        save_folder_id(request.user, 0)
        title = _('applications')
        hide_title = False
    else:
        title = context['site_header']
        hide_title = True

    context = get_base_context(request, 0, 0, title, 'content_list')
    context['title'] = title
    context['hide_title'] = hide_title
    context['trip_summary'] = trip_summary(request.user.id)
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Feedback
#----------------------------------
def feedback(request):
    context = get_base_context(request, 0, 0, _('feedback'))
    template = loader.get_template('feedback.html')
    return HttpResponse(template.render(context, request))


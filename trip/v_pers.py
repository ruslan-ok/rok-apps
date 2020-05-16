from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context, get_folder_id
from .models import Person
from .forms import PersonForm

def do_pers(request, pk):
    p = None
    if (request.method == 'GET'):
        if (pk != 0):
            p = get_object_or_404(Person, pk = pk)
            form = PersonForm(instance = p)
        else:
            form = PersonForm()
    else:
        if (pk != 0):
            p = get_object_or_404(Person, pk = pk)
        form = PersonForm(request.POST, instance = p)
        if form.is_valid():
            pers = form.save(commit = False)
            pers.user = request.user
            pers.save()
            return HttpResponseRedirect(reverse('trip:pers_list'))

    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, _('person'))
    context['form'] = form
    context['pers_id'] = pk
    context['me'] = get_me_code(request.user)
    return render(request, 'trip/person_form.html', context)

def get_me_code(_user):
    try:
        me = Person.objects.get(user = _user, me = 1)
        return me.id
    except Person.DoesNotExist:
        return 0

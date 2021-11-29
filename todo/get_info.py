from django.utils.translation import gettext_lazy as _
from rusel.files import get_files_list
from rusel.categories import get_categories_list
from task.models import TaskGroup, Urls, Step
from task.const import APP_TODO, ROLE_TODO

app = APP_TODO
role = ROLE_TODO

def get_info(item):
    ret = {'attr': []}
    
    if TaskGroup.objects.filter(task=item.id, role=role).exists():
        ret['group'] = TaskGroup.objects.filter(task=item.id, role=role).get().group.name

    if item.in_my_day:
        ret['attr'].append({'myday': True})

    step_total = 0
    step_completed = 0
    for step in Step.objects.filter(task=item.id):
        step_total += 1
        if step.completed:
            step_completed += 1
    if (step_total > 0):
        if (len(ret['attr']) > 0):
            ret['attr'].append({'icon': 'separator'})
        ret['attr'].append({'text': '{} {} {}'.format(step_completed, _('out of'), step_total)})

    if item.stop:
        ret['attr'].append({'termin': True})

    links = len(Urls.objects.filter(task=item.id)) > 0

    files = (len(get_files_list(item.user, app, role, item.id)) > 0)

    if (item.remind != None) or item.info or links or files:
        if (len(ret['attr']) > 0):
            ret['attr'].append({'icon': 'separator'})
        if (item.remind != None):
            ret['attr'].append({'icon': 'remind'})
        if links:
            ret['attr'].append({'icon': 'url'})
        if files:
            ret['attr'].append({'icon': 'attach'})
        if item.info:
            info_descr = item.info[:80]
            if len(item.info) > 80:
                info_descr += '...'
            ret['attr'].append({'icon': 'notes', 'text': info_descr})

    if item.categories:
        if (len(ret['attr']) > 0):
            ret['attr'].append({'icon': 'separator'})
        categs = get_categories_list(item.categories)
        for categ in categs:
            ret['attr'].append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})

    if item.completed:
        if (len(ret['attr']) > 0):
            ret['attr'].append({'icon': 'separator'})
        ret['attr'].append({'text': '{}: {}'.format(_('completion').capitalize(), item.completion.strftime('%d.%m.%Y') if item.completion else '')})

    return ret

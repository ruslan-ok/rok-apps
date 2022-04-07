from rusel.categories import get_categories_list
from task.models import TaskGroup, Urls
from task.const import APP_NOTE, ROLE_NOTE

app = APP_NOTE
role = ROLE_NOTE

def get_info(item):
    ret = {'attr': []}
    
    ret['attr'].append({'text': item.event.strftime('%d.%m.%Y %H:%M')})

    if TaskGroup.objects.filter(task=item.id, role=role).exists():
        ret['group'] = TaskGroup.objects.filter(task=item.id, role=role).get().group.name

    links = len(Urls.objects.filter(task=item.id)) > 0

    files = (len(item.get_files_list(app, role)) > 0)

    if item.info or links or files:
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

    return ret

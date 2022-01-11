from rusel.files import get_files_list
from rusel.categories import get_categories_list
from task.models import TaskGroup, Urls
from task.const import APP_STORE, ROLE_STORE

app = APP_STORE
role = ROLE_STORE

def get_info(item):
    ret = {'attr': []}
    
    if TaskGroup.objects.filter(task=item.id, role=role).exists():
        ret['group'] = TaskGroup.objects.filter(task=item.id, role=role).get().group.name

    ret['attr'].append({'text': '{} - {}'.format(item.store_username, '*'*len(item.store_value))})

    
    links = len(Urls.objects.filter(task=item.id)) > 0

    files = (len(get_files_list(item.user, app, role, item.id)) > 0)

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

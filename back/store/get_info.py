from task.models import Hist
from task.const import APP_STORE, ROLE_STORE

app = APP_STORE
role = ROLE_STORE

def get_info(item):
    attr = [{'text': '{} {}'.format(item.store_username, '*'*len(item.store_value))}]
    hist = Hist.objects.filter(task=item.id)
    if hist:
        attr.append({'text': '[{}]'.format(len(hist))})
    item.actualize_role_info(app, role, attr)

from task.const import APP_NOTE, ROLE_NOTE

app = APP_NOTE
role = ROLE_NOTE

def get_info(item):
    attr = [{'text': item.event.strftime('%d.%m.%Y %H:%M')}]
    item.actualize_role_info(app, role, attr)

from task.const import APP_NEWS, ROLE_NEWS

app = APP_NEWS
role = ROLE_NEWS

def get_info(item):
    attr = []
    if item.event:
        attr.append({'text': item.event.strftime('%d.%m.%Y %H:%M')})
    item.actualize_role_info(app, role, attr)

from task.const import APP_EXPEN, ROLE_EXPENSE

def get_info(item):
    attr = [{'text': ', '.join(item.expen_summary())}]
    item.actualize_role_info(APP_EXPEN, ROLE_EXPENSE, attr)


from task.const import APP_EXPEN, ROLE_EXPENSE

def get_info(item):
    it_sam = item.expen_item_summary()
    it_val = [x['value'] for x in it_sam]
    attr = []
    if len(it_val):
        attr = [{'text': ', '.join(it_val)}]
    item.actualize_role_info(APP_EXPEN, ROLE_EXPENSE, attr)

